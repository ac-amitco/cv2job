import asyncio
import logging

import httpx

from ..config import Settings
from ..schemas import Job
from .adzuna import AdzunaSource
from .arbeitnow import ArbeitnowSource
from .base import JobSource
from .jsearch import JSearchSource
from .remotive import RemotiveSource

logger = logging.getLogger(__name__)

SOURCES: list[JobSource] = [
    AdzunaSource(),
    JSearchSource(),
    RemotiveSource(),
    ArbeitnowSource(),
]

PER_SOURCE_TIMEOUT = 10.0


def list_sources(settings: Settings) -> list[dict]:
    return [{"id": s.id, "available": s.available(settings)} for s in SOURCES]


async def search_all(
    settings: Settings,
    query: str,
    location: str | None,
    remote: bool,
) -> tuple[list[Job], list[str], list[str]]:
    """Fan out to all enabled sources; a failing source never fails the request."""
    enabled = [s for s in SOURCES if s.available(settings)]
    async with httpx.AsyncClient(
        timeout=PER_SOURCE_TIMEOUT, follow_redirects=True
    ) as client:
        results = await asyncio.gather(
            *(s.search(client, settings, query, location, remote) for s in enabled),
            return_exceptions=True,
        )

    jobs: list[Job] = []
    used: list[str] = []
    failed: list[str] = []
    for source, result in zip(enabled, results):
        if isinstance(result, BaseException):
            logger.warning("job source %s failed: %s", source.id, result)
            failed.append(source.id)
        else:
            jobs.extend(result)
            used.append(source.id)
    return jobs, used, failed
