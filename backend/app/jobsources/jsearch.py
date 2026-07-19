import httpx

from ..config import Settings
from ..schemas import Job
from .base import clean_description, detect_country


class JSearchSource:
    """JSearch on RapidAPI — aggregates listings from LinkedIn, Indeed, Glassdoor etc."""

    id = "jsearch"

    def available(self, settings: Settings) -> bool:
        return bool(settings.rapidapi_key)

    async def search(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        query: str,
        location: str | None,
        remote: bool,
    ) -> list[Job]:
        search_query = f"{query} in {location}" if location else query
        params: dict = {"query": search_query, "num_pages": 1}
        country = detect_country(location)
        if country:
            params["country"] = country
        if remote:
            params["work_from_home"] = "true"
        resp = await client.get(
            "https://jsearch.p.rapidapi.com/search-v2",
            params=params,
            headers={
                "X-RapidAPI-Key": settings.rapidapi_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            },
        )
        resp.raise_for_status()
        # v2 wraps the list in {"data": {"jobs": [...]}}; older shape was a list.
        data = resp.json().get("data", {})
        items = data.get("jobs", []) if isinstance(data, dict) else data
        jobs = []
        for item in items:
            city = item.get("job_city")
            country = item.get("job_country")
            loc = ", ".join(part for part in (city, country) if part) or None
            salary = None
            if item.get("job_min_salary") and item.get("job_max_salary"):
                salary = (
                    f"{round(item['job_min_salary']):,} - "
                    f"{round(item['job_max_salary']):,}"
                )
            jobs.append(
                Job(
                    id=f"jsearch:{item.get('job_id', '')}",
                    title=item.get("job_title") or "",
                    company=item.get("employer_name") or "",
                    location=loc,
                    remote=item.get("job_is_remote"),
                    description=clean_description(item.get("job_description")),
                    url=item.get("job_apply_link") or "",
                    source=self.id,
                    posted_at=(item.get("job_posted_at_datetime_utc") or "")[:10] or None,
                    salary=salary,
                )
            )
        return jobs
