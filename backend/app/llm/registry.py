from ..config import Settings
from .anthropic_ import AnthropicClient
from .base import LLMClient
from .gemini import GeminiClient
from .openai_ import OpenAIClient

PROVIDERS: dict[str, dict] = {
    "gemini": {
        "label": "Gemini 2.0 Flash",
        "model": "gemini-2.0-flash",
        "key_attr": "gemini_api_key",
        "factory": GeminiClient,
        "default": True,
    },
    "claude": {
        "label": "Claude Haiku 4.5",
        "model": "claude-haiku-4-5",
        "key_attr": "anthropic_api_key",
        "factory": AnthropicClient,
        "default": False,
    },
    "openai": {
        "label": "GPT-4o mini",
        "model": "gpt-4o-mini",
        "key_attr": "openai_api_key",
        "factory": OpenAIClient,
        "default": False,
    },
}


def provider_available(settings: Settings, name: str) -> bool:
    info = PROVIDERS.get(name)
    if info is None:
        return False
    return bool(getattr(settings, info["key_attr"]))


def get_client(settings: Settings, name: str) -> LLMClient | None:
    """Client for the requested provider, or None when it isn't configured."""
    if not provider_available(settings, name):
        return None
    info = PROVIDERS[name]
    api_key = getattr(settings, info["key_attr"])
    return info["factory"](api_key=api_key, model=info["model"])


def list_providers(settings: Settings) -> list[dict]:
    return [
        {
            "id": name,
            "label": info["label"],
            "model": info["model"],
            "available": provider_available(settings, name),
            "default": info["default"],
        }
        for name, info in PROVIDERS.items()
    ]
