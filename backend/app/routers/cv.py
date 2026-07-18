import logging

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from ..config import Settings, get_settings
from ..llm.base import LLMError
from ..llm.registry import get_client
from ..schemas import ParseResponse
from ..services.extraction import ExtractionError, extract_text
from ..services.profile import build_profile_lexical, build_profile_llm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cv"])


@router.post("/cv/parse")
async def parse_cv(
    file: UploadFile,
    model: str = Form("gemini"),
    settings: Settings = Depends(get_settings),
) -> ParseResponse:
    data = await file.read()
    try:
        text = extract_text(file.filename or "", data)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    client = get_client(settings, model)
    if client is not None:
        try:
            profile = await build_profile_llm(client, text)
            return ParseResponse(profile=profile, raw_text_chars=len(text), used_llm=True)
        except LLMError as exc:
            logger.warning("LLM profile extraction failed, using lexical fallback: %s", exc)

    profile = build_profile_lexical(text)
    return ParseResponse(profile=profile, raw_text_chars=len(text), used_llm=False)
