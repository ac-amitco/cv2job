import re

import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description

# Adzuna serves per-country endpoints; map common location mentions to a
# country code, defaulting to the US.
_COUNTRY_PATTERNS: list[tuple[str, str]] = [
    (r"\b(uk|united kingdom|london|manchester|england)\b", "gb"),
    (r"\b(germany|berlin|munich|hamburg)\b", "de"),
    (r"\b(france|paris)\b", "fr"),
    (r"\b(netherlands|amsterdam)\b", "nl"),
    (r"\b(canada|toronto|vancouver)\b", "ca"),
    (r"\b(australia|sydney|melbourne)\b", "au"),
    (r"\b(india|bangalore|bengaluru|mumbai|delhi)\b", "in"),
    (r"\b(usa|us|united states|new york|san francisco|remote us)\b", "us"),
]


def _country_for(location: str | None) -> str:
    lower = (location or "").lower()
    for pattern, code in _COUNTRY_PATTERNS:
        if re.search(pattern, lower):
            return code
    return "us"


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
        country = _country_for(location)
        params = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "what": query,
            "results_per_page": 50,
        }
        if location:
            params["where"] = location
        resp = await client.get(
            f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
            params=params,
        )
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("results", []):
            salary = None
            if item.get("salary_min") or item.get("salary_max"):
                low = item.get("salary_min")
                high = item.get("salary_max")
                salary = f"{round(low):,} - {round(high):,}" if low and high else None
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
