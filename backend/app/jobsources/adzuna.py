import logging

import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description, detect_country

logger = logging.getLogger(__name__)

# Adzuna serves per-country endpoints for these markets only.
SUPPORTED_COUNTRIES = {
    "at", "au", "be", "br", "ca", "ch", "de", "es", "fr", "gb",
    "in", "it", "mx", "nl", "nz", "pl", "sg", "us", "za",
}


class AdzunaSource:
    id = "adzuna"

    def available(self, settings: Settings) -> bool:
        return bool(settings.adzuna_app_id and settings.adzuna_app_key)

    async def search(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        query: str,
        location: str | None,
        remote: bool,
    ) -> list[Job]:
        country = detect_country(location)
        if location and country is None:
            # Unknown market — searching a default country would return
            # irrelevant jobs, so contribute nothing instead.
            logger.info("adzuna: unrecognized location %r, skipping", location)
            return []
        if country and country not in SUPPORTED_COUNTRIES:
            logger.info("adzuna: no coverage for country %r, skipping", country)
            return []

        params = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "what": query,
            "results_per_page": 50,
        }
        if location:
            params["where"] = location
        resp = await client.get(
            f"https://api.adzuna.com/v1/api/jobs/{country or 'us'}/search/1",
            params=params,
        )
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("results", []):
            salary = None
            low = item.get("salary_min")
            high = item.get("salary_max")
            if low and high:
                salary = f"{round(low):,} - {round(high):,}"
            jobs.append(
                Job(
                    id=f"adzuna:{item.get('id', '')}",
                    title=item.get("title") or "",
                    company=(item.get("company") or {}).get("display_name") or "",
                    location=(item.get("location") or {}).get("display_name"),
                    remote=None,
                    description=clean_description(item.get("description")),
                    url=item.get("redirect_url") or "",
                    source=self.id,
                    posted_at=(item.get("created") or "")[:10] or None,
                    salary=salary,
                )
            )
        return jobs
