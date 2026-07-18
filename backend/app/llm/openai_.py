from typing import Any

import openai

from .base import LLMError, parse_json_text


class OpenAIClient:
    provider = "openai"

    def __init__(self, api_key: str, model: str):
        self._client = openai.AsyncOpenAI(api_key=api_key)
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
            response_format: dict = {
                "type": "json_schema",
                "json_schema": {"name": "result", "strict": True, "schema": schema},
            }
        else:
            response_format = {"type": "json_object"}
            system = f"{system}\n\nRespond with only valid JSON."
        try:
            resp = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                response_format=response_format,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except openai.OpenAIError as exc:
            raise LLMError(f"OpenAI request failed: {exc}") from exc
        return parse_json_text(resp.choices[0].message.content)
