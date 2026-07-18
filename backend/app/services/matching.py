import asyncio
import json
import logging
import time

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..config import Settings
from ..jobsources.aggregator import search_all
from ..llm.base import LLMClient, LLMError, strict_schema
from ..llm.registry import get_client
from ..schemas import CVProfile, Job, MatchedJob, MatchRequest, MatchResponse
from .dedupe import dedupe

logger = logging.getLogger(__name__)

PREFILTER_LIMIT = 40
SCORING_BATCH_SIZE = 10
SCORING_DESCRIPTION_CHARS = 600

SCORING_SYSTEM = (
    "You are a recruiting assistant. Score how well each job listing matches "
    "the candidate profile, from 0 (no fit) to 100 (excellent fit). Consider "
    "role match, skill overlap, seniority and location/remote fit. For each "
    "job, give a short 1-2 sentence 'why' explaining the fit (or lack of it) "
    "referencing the candidate's actual skills. Return one entry per job id."
)


class JobScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    score: int = Field(ge=0, le=100)
    why: str


class JobScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: list[JobScore]


def build_query(profile: CVProfile) -> str:
    if profile.titles:
        return profile.titles[0]
    if profile.skills:
        return " ".join(profile.skills[:3])
    return "software developer"


def lexical_score(
    profile: CVProfile, job: Job, remote_only: bool
) -> tuple[float, list[str]]:
    """Weighted keyword overlap between profile and job. Returns (0..1, matched terms)."""
    text = f"{job.title} {job.description}".lower()
    title_text = job.title.lower()

    points = 0.0
    possible = 0.0
    matched: list[str] = []

    for title in profile.titles:
        possible += 3.0
        t = title.lower().strip()
        if not t:
            continue
        if t in title_text:
            points += 3.0
            matched.append(title)
        elif t in text:
            points += 1.5
            matched.append(title)

    for skill in profile.skills:
        possible += 1.0
        s = skill.lower().strip()
        if s and s in text:
            points += 1.0
            matched.append(skill)

    if possible == 0:
        return 0.0, []

    score = points / possible
    if remote_only and job.remote:
        score = min(1.0, score + 0.05)
    return score, matched


def _compact_profile(profile: CVProfile) -> str:
    return json.dumps(
        {
            "titles": profile.titles,
            "skills": profile.skills,
            "seniority": profile.seniority,
            "experience_years": profile.experience_years,
            "locations": profile.locations,
            "summary": profile.summary,
        },
        ensure_ascii=False,
    )


async def _score_batch(
    client: LLMClient, profile_json: str, jobs: list[Job]
) -> dict[str, tuple[int, str]]:
    jobs_json = json.dumps(
        [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "remote": j.remote,
                "description": j.description[:SCORING_DESCRIPTION_CHARS],
            }
            for j in jobs
        ],
        ensure_ascii=False,
    )
    user = f"Candidate profile:\n{profile_json}\n\nJobs to score:\n{jobs_json}"
    result = await client.complete_json(
        system=SCORING_SYSTEM, user=user, schema=strict_schema(JobScores)
    )
    try:
        validated = JobScores.model_validate(result)
    except ValidationError as exc:
        raise LLMError(f"Scoring response failed validation: {exc}") from exc
    return {s.id: (s.score, s.why) for s in validated.scores}


async def match_jobs(settings: Settings, req: MatchRequest) -> MatchResponse:
    started = time.monotonic()
    query = build_query(req.profile)

    raw_jobs, used, failed = await search_all(
        settings, query, req.location, req.remote_only
    )
    jobs = dedupe(raw_jobs)
    if req.remote_only:
        jobs = [j for j in jobs if j.remote is not False]

    # Cheap lexical pre-filter; also the fallback score when the LLM is unavailable.
    prefiltered = sorted(
        ((lexical_score(req.profile, job, req.remote_only), job) for job in jobs),
        key=lambda pair: pair[0][0],
        reverse=True,
    )[:PREFILTER_LIMIT]

    client = get_client(settings, req.model)
    llm_scores: dict[str, tuple[int, str]] = {}
    if client is not None and prefiltered:
        profile_json = _compact_profile(req.profile)
        batches = [
            [job for _, job in prefiltered[i : i + SCORING_BATCH_SIZE]]
            for i in range(0, len(prefiltered), SCORING_BATCH_SIZE)
        ]
        results = await asyncio.gather(
            *(_score_batch(client, profile_json, batch) for batch in batches),
            return_exceptions=True,
        )
        for batch, result in zip(batches, results):
            if isinstance(result, BaseException):
                logger.warning("scoring batch failed, using lexical fallback: %s", result)
            else:
                llm_scores.update(result)

    matched = []
    for (lex_score, terms), job in prefiltered:
        if job.id in llm_scores:
            score, why = llm_scores[job.id]
        else:
            score = round(lex_score * 100)
            why = (
                f"Keyword match on: {', '.join(dict.fromkeys(terms))}"
                if terms
                else "No direct keyword overlap with your profile."
            )
        matched.append(MatchedJob(**job.model_dump(), score=score, why=why))
    matched.sort(key=lambda j: j.score, reverse=True)

    used_llm = bool(llm_scores)
    logger.info(
        "match: query=%r model=%s llm=%s sources=%s failed=%s raw=%d deduped=%d in %.1fs",
        query, req.model, used_llm, used, failed,
        len(raw_jobs), len(jobs), time.monotonic() - started,
    )
    return MatchResponse(
        jobs=matched[: req.limit],
        sources_used=used,
        sources_failed=failed,
        used_llm=used_llm,
    )
