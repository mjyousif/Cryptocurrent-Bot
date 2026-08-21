"""Google AI / Gemini client (data layer).

Provides a thin wrapper to call the Gemini / Generative API.
We now use `litellm` under the hood to unify our LLM interactions.

Environment variables supported:
- GEMINI_API_KEY: (required) API key; will be used by litellm for gemini/ models

Usage:
    from data.google_ai import generate_text

    text = generate_text("Write me a short crypto market summary")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    import litellm
except ImportError as exc:
    raise ImportError(
        "litellm is required for LLM support. Install with: uv add litellm"
    ) from exc

logger = logging.getLogger(__name__)

# Default model to use (we will prefix with gemini/ for litellm)
DEFAULT_MODEL = "gemini-3.1-flash-lite"


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
    """Generate text using LiteLLM (routing to Gemini by default).

    Args:
        prompt: the input text prompt.
        model: model name (defaults to gemma-3-27b-it).
        temperature: randomness control (0.0 = deterministic).
        max_output_tokens: maximum tokens for the generated output.
        candidate_count: how many candidates to request. (litellm supports n=...)
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

    # If the user didn't prefix the model, assume gemini/
    if not model.startswith("gemini/") and not model.startswith("vertex_ai/"):
        model = f"gemini/{model}"

    logger.debug(
        "Calling litellm.completion with model=%s and prompt=%s",
        model,
        prompt,
    )

    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_output_tokens,
            top_p=top_p,
            timeout=timeout,
        )
    except Exception as exc:
        logger.exception("Error when calling litellm")
        raise GoogleAIError(f"Error when calling litellm: {exc}") from exc

    text = response.choices[0].message.content
    if text is None:
        logger.error("LiteLLM response missing content: %s", response)
        raise GoogleAIError("Unexpected SDK response format")

    try:
        preview = text if len(text) <= 300 else text[:300] + "..."
    except Exception:
        preview = "<unavailable>"
    logger.debug("Google AI response (truncated 300): %s", preview)

    return text


class Response:
    """Small compatibility response object."""
    def __init__(self, text: str):
        self.text = text


class _Models:
    def generate_content(
        self,
        model: str = DEFAULT_MODEL,
        contents: Any = None,
        **kwargs
    ) -> Response:
        """Gemini-style generate_content compatible method (uses SDK directly)."""
        if contents is None:
            raise GoogleAIError("contents is required")
        prompt = (
            contents if isinstance(contents, str) else "\n".join(map(str, contents))
        )
        text = generate_text(prompt=prompt, model=model, **kwargs)
        return Response(text=text)


class Client:
    """Lightweight client compatible with the Gemini quickstart usage."""
    def __init__(self):
        self.models = _Models()


def generate_content(*args, **kwargs):
    """Dual-mode helper."""
    if "contents" in kwargs:
        model = kwargs.pop("model", DEFAULT_MODEL)
        contents = kwargs.pop("contents")
        return Client().models.generate_content(
            model=model, contents=contents, **kwargs
        )
    return generate_text(*args, **kwargs)
