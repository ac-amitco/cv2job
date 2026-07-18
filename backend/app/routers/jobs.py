from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..schemas import MatchRequest, MatchResponse
from ..services.matching import match_jobs

router = APIRouter(tags=["jobs"])


@router.post("/jobs/match")
async def match(
    req: MatchRequest,
    settings: Settings = Depends(get_settings),
) -> MatchResponse:
    return await match_jobs(settings, req)
