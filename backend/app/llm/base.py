import json
import re
from typing import Any, Protocol

from pydantic import BaseModel


class LLMError(Exception):
    """Raised when an LLM provider call fails or returns unusable output."""


class LLMClient(Protocol):
    provider: str

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: dict | None = None,
        max_tokens: int = 2048,
    ) -> Any: ...


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

# JSON-schema keywords not supported by provider structured-output modes
# (Anthropic rejects numeric/length constraints; OpenAI strict mode requires
# additionalProperties: false and every property listed in required).
_UNSUPPORTED_KEYS = {
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minLength", "maxLength", "multipleOf", "minItems", "maxItems", "default",
}


def parse_json_text(text: str | None) -> Any:
    if not text:
        raise LLMError("Model returned an empty response.")
    cleaned = _FENCE_RE.sub("", text.strip()).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model returned invalid JSON: {cleaned[:200]}") from exc


def strict_schema(model: type[BaseModel]) -> dict:
    """JSON schema for `model`, normalized for provider structured-output modes."""
    schema = model.model_json_schema()
    _normalize(schema)
    return schema


def _normalize(node: Any) -> None:
    if isinstance(node, dict):
        for key in _UNSUPPORTED_KEYS:
            node.pop(key, None)
        if node.get("type") == "object" and "properties" in node:
            node["additionalProperties"] = False
            node["required"] = list(node["properties"])
        for value in node.values():
            _normalize(value)
    elif isinstance(node, list):
        for item in node:
            _normalize(item)
