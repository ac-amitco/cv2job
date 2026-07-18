from typing import Any

from google import genai
from google.genai import types as genai_types

from .base import LLMError, parse_json_text


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
        try:
            resp = await self._client.aio.models.generate_content(
                model=self._model,
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
