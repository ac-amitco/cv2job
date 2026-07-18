import html
import re
from typing import Protocol

import httpx

from ..config import Settings
from ..schemas import Job

DESCRIPTION_LIMIT = 1500

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
