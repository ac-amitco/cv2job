import re

from rapidfuzz import fuzz

from ..schemas import Job

_NORM_RE = re.compile(r"[^a-z0-9 ]")

# Lower value = preferred origin when two listings collide (direct boards first).
_SOURCE_PRIORITY = {"adzuna": 0, "jsearch": 1, "remotive": 2, "arbeitnow": 3}

FUZZY_TITLE_THRESHOLD = 90


def _norm(text: str) -> str:
    return _NORM_RE.sub("", text.lower()).strip()


def _richness(job: Job) -> tuple:
    return (
        len(job.description),
        job.salary is not None,
        -_SOURCE_PRIORITY.get(job.source, 99),
    )


def dedupe(jobs: list[Job]) -> list[Job]:
    """Drop duplicate listings, keeping the richest entry per (title, company)."""
    by_key: dict[str, Job] = {}
    for job in jobs:
        key = f"{_norm(job.title)}|{_norm(job.company)}"
        existing = by_key.get(key)
        if existing is None or _richness(job) > _richness(existing):
            by_key[key] = job

    by_company: dict[str, list[Job]] = {}
    for job in by_key.values():
        by_company.setdefault(_norm(job.company), []).append(job)

    result: list[Job] = []
    for company_jobs in by_company.values():
        kept: list[Job] = []
        for job in sorted(company_jobs, key=_richness, reverse=True):
            title = _norm(job.title)
            if any(
                fuzz.token_sort_ratio(title, _norm(k.title)) >= FUZZY_TITLE_THRESHOLD
                for k in kept
            ):
                continue
            kept.append(job)
        result.extend(kept)
    return result
