from ..config import Settings

PROVIDERS: dict[str, dict] = {
    "gemini": {
        "label": "Gemini 2.0 Flash",
        "model": "gemini-2.0-flash",
        "key_attr": "gemini_api_key",
        "default": True,
    },
    "claude": {
        "label": "Claude 3.5 Haiku",
        "model": "claude-3-5-haiku-latest",
        "key_attr": "anthropic_api_key",
        "default": False,
    },
    "openai": {
        "label": "GPT-4o mini",
        "model": "gpt-4o-mini",
        "key_attr": "openai_api_key",
        "default": False,
    },
}


def provider_available(settings: Settings, name: str) -> bool:
    info = PROVIDERS.get(name)
    if info is None:
        return False
    return bool(getattr(settings, info["key_attr"]))


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
