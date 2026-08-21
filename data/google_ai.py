"""Google AI / Gemini client (data layer).

Provides a thin wrapper to call the Gemini / Generative API. This client uses a simple
API-key based authentication and is intentionally lightweight so it doesn't require the
official SDK as a dependency.

Environment variables supported:
- GEMINI_API_KEY: (required) API key; will be sent as ?key=... query parameter

Note: This client only supports API key authentication; access-token and ADC-based methods were removed.

Usage:
    from data.google_ai import generate_text

    text = generate_text("Write me a short crypto market summary")

"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from google import genai
except Exception as exc:
    raise ImportError(
        "google-genai is required for Google AI support. Install with: uv add google-genai"
    ) from exc

# Preserve backward compatibility for env var name
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

logger = logging.getLogger(__name__)

# Default model to use
DEFAULT_MODEL = "gemma-3-27b-it"


class GoogleAIError(RuntimeError):
    pass


def generate_text(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_output_tokens: int = 512,
    candidate_count: int = 1,
    top_p: Optional[float] = None,
    safety_settings: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> str:
    """Generate text using Google Generative Language API.

    Args:
        prompt: the input text prompt.
        model: model name (defaults to gemma-3-27b).
        temperature: randomness control (0.0 = deterministic).
        max_output_tokens: maximum tokens for the generated output.
        candidate_count: how many candidates to request; we return the first one.
        top_p: optional nucleus sampling parameter.
        safety_settings: optional dictionary to pass to the API's safety settings.
        timeout: HTTP request timeout in seconds.

    Returns:
        The generated text (string).

    Raises:
        GoogleAIError on non-success or unexpected responses.
    """

    if not prompt:
        raise ValueError("prompt must be a non-empty string")

    # Use the official google-genai SDK client
    try:
        client = genai.Client()
    except Exception as exc:
        logger.exception("Failed to initialize google-genai Client")
        raise GoogleAIError("Failed to initialize Google GenAI client") from exc

    sdk_kwargs: Dict[str, Any] = {"model": model, "contents": prompt}

    logger.debug(
        "Calling google-genai SDK models.generate_content with model=%s and propmts=%s",
        model,
        prompt,
    )

    try:
        resp = client.models.generate_content(**sdk_kwargs)
    except Exception as exc:
        logger.exception("Error when calling Google GenAI SDK")
        raise GoogleAIError("Error when calling Google GenAI SDK") from exc

    # SDK responses commonly have a `.text` attribute
    text = getattr(resp, "text", None)
    if text is None:
        logger.error("SDK response missing .text: %s", resp)
        raise GoogleAIError("Unexpected SDK response format")

    # Log the SDK response for debugging (truncated to 300 chars)
    try:
        preview = text if len(text) <= 300 else text[:300] + "..."
    except Exception:
        preview = "<unavailable>"
    logger.debug("Google AI response (truncated 300): %s", preview)

    return text


@dataclass
class Response:
    """Small compatibility response object similar to SDK responses."""

    text: str


class _Models:
    def generate_content(
        self,
        model: str = DEFAULT_MODEL,
        contents: Any = None,
        temperature: float = 0.0,
        max_output_tokens: int = 512,
        candidate_count: int = 1,
        top_p: Optional[float] = None,
        safety_settings: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Response:
        """Gemini-style generate_content compatible method (uses SDK directly).

        Args:
            model: Model name (e.g., 'gemma-3-27b').
            contents: A string or list of strings to use as the prompt(s).

        Returns:
            A `Response` object with `.text` containing the generated content.
        """
        if contents is None:
            raise GoogleAIError("contents is required")
        prompt = (
            contents if isinstance(contents, str) else "\n".join(map(str, contents))
        )

        try:
            client = genai.Client()
        except Exception as exc:
            logger.exception("Failed to initialize google-genai Client")
            raise GoogleAIError("Failed to initialize Google GenAI client") from exc

        sdk_kwargs: Dict[str, Any] = {"model": model, "contents": prompt}
        if temperature is not None:
            sdk_kwargs["temperature"] = temperature
        if max_output_tokens is not None:
            sdk_kwargs["max_output_tokens"] = max_output_tokens
        if candidate_count is not None:
            sdk_kwargs["candidate_count"] = candidate_count
        if top_p is not None:
            sdk_kwargs["top_p"] = top_p
        if safety_settings is not None:
            sdk_kwargs["safety_settings"] = safety_settings

        try:
            resp = client.models.generate_content(**sdk_kwargs)
        except Exception as exc:
            logger.exception("Error when calling Google GenAI SDK")
            raise GoogleAIError("Error when calling Google GenAI SDK") from exc

        text = getattr(resp, "text", None)
        if text is None:
            logger.error("SDK response missing .text: %s", resp)
            raise GoogleAIError("Unexpected SDK response format")

        # Log the SDK response for debugging (truncated to 300 chars)
        try:
            preview = text if len(text) <= 300 else text[:300] + "..."
        except Exception:
            preview = "<unavailable>"
        logger.debug(
            "Google AI response (models.generate_content, truncated 300): %s", preview
        )

        return Response(text=text)


class Client:
    """Lightweight client compatible with the Gemini quickstart usage.

    Example:
        from data.google_ai import Client
        client = Client()
        resp = client.models.generate_content(model="gemma-3-27b", contents="Explain AI in a few words")
        print(resp.text)
    """

    def __init__(self):
        self.models = _Models()


def generate_content(*args, **kwargs):
    """Dual-mode helper:

    - If called like the old alias (generate_content(prompt, ...)) it behaves like `generate_text` and returns a `str`.
    - If called with `contents=` keyword (generate_content(contents=..., model=...)) it returns a `Response` with `.text`.

    This keeps backward compatibility while supporting the Gemini-style API.
    """
    # Gemini-style: keyword contents -> return Response
    if "contents" in kwargs:
        model = kwargs.pop("model", DEFAULT_MODEL)
        contents = kwargs.pop("contents")
        return Client().models.generate_content(
            model=model, contents=contents, **kwargs
        )

    # Legacy-style: positional prompt -> return str
    return generate_text(*args, **kwargs)


if __name__ == "__main__":
    # Quick manual test (only when run directly) - requires GEMINI_API_KEY
    logging.basicConfig(level=logging.DEBUG)
    try:
        out = generate_text(
            "Say hello from a crypto bot and mention BTC and ETH in one sentence."
        )
        print("Generated:\n", out)
    except Exception as exc:
        print("Error:", exc)
