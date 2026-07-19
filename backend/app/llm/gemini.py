import logging
from typing import Any

from google import genai
from google.genai import types as genai_types

from .base import LLMError, parse_json_text

logger = logging.getLogger(__name__)

# Free-tier daily quotas are per model, so when the primary model's quota is
# exhausted (429) we retry on lighter models with their own, larger quotas.
FALLBACK_MODELS = ("gemini-3.1-flash-lite",)


class GeminiClient:
    provider = "gemini"

    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: dict | None = None,
        max_tokens: int = 2048,
    ) -> Any:
        if schema is not None:
            system = f"{system}\n\nRespond with JSON matching this schema:\n{schema}"
        last_error: LLMError | None = None
        for model in (self._model, *FALLBACK_MODELS):
            try:
                return await self._generate(model, system, user, max_tokens)
            except LLMError as exc:
                if "429" not in str(exc):
                    raise
                logger.warning("gemini model %s rate-limited, trying fallback", model)
                last_error = exc
        raise last_error  # type: ignore[misc]  # loop always runs at least once

    async def _generate(
        self, model: str, system: str, user: str, max_tokens: int
    ) -> Any:
        try:
            resp = await self._client.aio.models.generate_content(
                model=model,
                contents=user,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    max_output_tokens=max_tokens,
                ),
            )
        except Exception as exc:
            raise LLMError(f"Gemini request failed: {exc}") from exc
        return parse_json_text(resp.text)
