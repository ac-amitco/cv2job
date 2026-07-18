import logging
import time

from ..config import Settings
from ..jobsources.aggregator import search_all
from ..schemas import CVProfile, Job, MatchedJob, MatchRequest, MatchResponse
from .dedupe import dedupe

logger = logging.getLogger(__name__)

PREFILTER_LIMIT = 40


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


async def match_jobs(settings: Settings, req: MatchRequest) -> MatchResponse:
    started = time.monotonic()
    query = build_query(req.profile)

    raw_jobs, used, failed = await search_all(
        settings, query, req.location, req.remote_only
    )
    jobs = dedupe(raw_jobs)
    if req.remote_only:
        jobs = [j for j in jobs if j.remote is not False]

    scored = sorted(
        ((lexical_score(req.profile, job, req.remote_only), job) for job in jobs),
        key=lambda pair: pair[0][0],
        reverse=True,
    )[:PREFILTER_LIMIT]

    matched = [
        MatchedJob(
            **job.model_dump(),
            score=round(score * 100),
            why=(
                f"Keyword match on: {', '.join(dict.fromkeys(terms))}"
                if terms
                else "No direct keyword overlap with your profile."
            ),
        )
        for (score, terms), job in scored
    ]
    matched.sort(key=lambda j: j.score, reverse=True)

    logger.info(
        "match: query=%r sources=%s failed=%s raw=%d deduped=%d returned=%d in %.1fs",
        query, used, failed, len(raw_jobs), len(jobs),
        min(len(matched), req.limit), time.monotonic() - started,
    )
    return MatchResponse(
        jobs=matched[: req.limit],
        sources_used=used,
        sources_failed=failed,
        used_llm=False,
    )
