from functools import lru_cache

from google import genai

from .config import get_settings


class AIConfigurationError(RuntimeError):
    """Raised when Gemini cannot be configured."""


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise AIConfigurationError(
            "GEMINI_API_KEY is not configured. "
            "Add it to .env or enable MOCK_AI=true for local testing."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(
    model: str,
    prompt: str,
    temperature: float = 0.6,
    max_output_tokens: int = 5000,
) -> str:

    client = get_gemini_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
    )

    text = (
        response.text or ""
    ).strip()

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text