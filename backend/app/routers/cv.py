from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from ..config import Settings, get_settings
from ..schemas import ParseResponse
from ..services.extraction import ExtractionError, extract_text
from ..services.profile import build_profile_lexical

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

    profile = build_profile_lexical(text)
    return ParseResponse(profile=profile, raw_text_chars=len(text), used_llm=False)
