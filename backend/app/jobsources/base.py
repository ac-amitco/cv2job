import html
import re
from typing import Protocol

import httpx

from ..config import Settings
from ..schemas import Job

DESCRIPTION_LIMIT = 1500

# Map location mentions to ISO 3166-1 alpha-2 country codes so sources that
# support country filtering return local jobs.
_LOCATION_COUNTRIES: list[tuple[str, str]] = [
    (r"\b(israel|tel aviv|jerusalem|haifa|beer ?sheva|herzliya|ramat gan)\b", "il"),
    (r"\b(uk|united kingdom|london|manchester|england|scotland)\b", "gb"),
    (r"\b(germany|berlin|munich|hamburg|frankfurt)\b", "de"),
    (r"\b(france|paris|lyon)\b", "fr"),
    (r"\b(netherlands|amsterdam|rotterdam)\b", "nl"),
    (r"\b(spain|madrid|barcelona)\b", "es"),
    (r"\b(italy|milan|rome)\b", "it"),
    (r"\b(poland|warsaw|krakow)\b", "pl"),
    (r"\b(switzerland|zurich|geneva)\b", "ch"),
    (r"\b(austria|vienna)\b", "at"),
    (r"\b(canada|toronto|vancouver|montreal)\b", "ca"),
    (r"\b(australia|sydney|melbourne)\b", "au"),
    (r"\b(india|bangalore|bengaluru|mumbai|delhi|hyderabad)\b", "in"),
    (r"\b(singapore)\b", "sg"),
    (r"\b(brazil|sao paulo)\b", "br"),
    (r"\b(mexico|mexico city)\b", "mx"),
    (r"\b(usa|us|united states|new york|san francisco|seattle|austin|boston)\b", "us"),
]


def detect_country(location: str | None) -> str | None:
    """Best-effort ISO country code for a free-text location, or None."""
    lower = (location or "").lower()
    for pattern, code in _LOCATION_COUNTRIES:
        if re.search(pattern, lower):
            return code
    return None

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_description(text: str | None, limit: int = DESCRIPTION_LIMIT) -> str:
    text = html.unescape(text or "")
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text[:limit]


class JobSource(Protocol):
    id: str

    def available(self, settings: Settings) -> bool: ...

    async def search(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        query: str,
        location: str | None,
        remote: bool,
    ) -> list[Job]: ...
