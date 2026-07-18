import pytest
from pydantic import BaseModel, ConfigDict, Field

from app.llm.base import LLMError, parse_json_text, strict_schema


class Inner(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)


class Outer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[Inner]
    name: str


def test_strict_schema_strips_unsupported_constraints():
    schema = strict_schema(Outer)
    inner = schema["$defs"]["Inner"]
    assert "minimum" not in inner["properties"]["score"]
    assert "maximum" not in inner["properties"]["score"]


def test_strict_schema_forbids_extra_and_requires_all():
    schema = strict_schema(Outer)
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"items", "name"}
    inner = schema["$defs"]["Inner"]
    assert inner["additionalProperties"] is False
    assert inner["required"] == ["score"]


def test_parse_json_text_plain():
    assert parse_json_text('{"a": 1}') == {"a": 1}


def test_parse_json_text_strips_markdown_fences():
    assert parse_json_text('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_text_rejects_empty_and_invalid():
    with pytest.raises(LLMError):
        parse_json_text("")
    with pytest.raises(LLMError):
        parse_json_text("not json at all")
