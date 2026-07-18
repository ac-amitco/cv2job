from datetime import datetime, timezone

import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description


class ArbeitnowSource:
    id = "arbeitnow"

    def available(self, settings: Settings) -> bool:
        return True

    async def search(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        query: str,
        location: str | None,
        remote: bool,
    ) -> list[Job]:
        resp = await client.get(
            "https://www.arbeitnow.com/api/job-board-api",
            params={"search": query},
        )
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("data", []):
            created = item.get("created_at")
            posted_at = (
                datetime.fromtimestamp(created, tz=timezone.utc).date().isoformat()
                if isinstance(created, (int, float))
                else None
            )
            jobs.append(
                Job(
                    id=f"arbeitnow:{item.get('slug', '')}",
                    title=item.get("title") or "",
                    company=item.get("company_name") or "",
                    location=item.get("location") or None,
                    remote=item.get("remote"),
                    description=clean_description(item.get("description")),
                    url=item.get("url") or "",
                    source=self.id,
                    posted_at=posted_at,
                    salary=None,
                )
            )
        return jobs
