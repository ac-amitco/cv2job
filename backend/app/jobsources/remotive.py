import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description


class RemotiveSource:
    id = "remotive"

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
            "https://remotive.com/api/remote-jobs",
            params={"search": query, "limit": 50},
        )
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("jobs", []):
            jobs.append(
                Job(
                    id=f"remotive:{item['id']}",
                    title=item.get("title") or "",
                    company=item.get("company_name") or "",
                    location=item.get("candidate_required_location") or None,
                    remote=True,
                    description=clean_description(item.get("description")),
                    url=item.get("url") or "",
                    source=self.id,
                    posted_at=item.get("publication_date") or None,
                    salary=item.get("salary") or None,
                )
            )
        return jobs
