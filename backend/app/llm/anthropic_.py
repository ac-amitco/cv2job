from typing import Any

import anthropic

from .base import LLMError, parse_json_text


class AnthropicClient:
    provider = "claude"

    def __init__(self, api_key: str, model: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: dict | None = None,
        max_tokens: int = 2048,
    ) -> Any:
        kwargs: dict = {}
        if schema is not None:
            kwargs["output_config"] = {
                "format": {"type": "json_schema", "schema": schema}
            }
        else:
            system = f"{system}\n\nRespond with only valid JSON, no other text."
        try:
            resp = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                **kwargs,
            )
        except anthropic.APIError as exc:
            raise LLMError(f"Claude request failed: {exc}") from exc
        text = next((b.text for b in resp.content if b.type == "text"), None)
        return parse_json_text(text)
