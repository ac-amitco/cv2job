import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description, detect_country

# Jooble serves per-country subdomains; the bare domain covers the US/intl.
_SUBDOMAINS = {"gb": "uk", "us": None}


def _host(location: str | None) -> str:
    country = detect_country(location)
    sub = _SUBDOMAINS.get(country, country) if country else None
    return f"{sub}.jooble.org" if sub else "jooble.org"


class JoobleSource:
    """Jooble aggregator — notable for covering markets the other sources
    miss (e.g. Israel via il.jooble.org). Free key at jooble.org/api/about."""

    id = "jooble"

    def available(self, settings: Settings) -> bool:
        return bool(settings.jooble_api_key)

    async def search(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        query: str,
        location: str | None,
        remote: bool,
    ) -> list[Job]:
        payload: dict = {"keywords": query}
        if location:
            payload["location"] = location
        resp = await client.post(
            f"https://{_host(location)}/api/{settings.jooble_api_key}",
            json=payload,
        )
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("jobs", []):
            jobs.append(
                Job(
                    id=f"jooble:{item.get('id', '')}",
                    title=item.get("title") or "",
                    company=item.get("company") or "",
                    location=item.get("location") or None,
                    remote=None,
                    description=clean_description(item.get("snippet")),
                    url=item.get("link") or "",
                    source=self.id,
                    posted_at=(item.get("updated") or "")[:10] or None,
                    salary=item.get("salary") or None,
                )
            )
        return jobs
