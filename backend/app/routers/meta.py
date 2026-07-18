from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..jobsources.aggregator import list_sources
from ..llm.registry import list_providers

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/providers")
def providers(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "llm": list_providers(settings),
        "job_sources": list_sources(settings),
    }
