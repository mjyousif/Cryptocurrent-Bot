from unittest.mock import MagicMock, patch

import pytest

from data.google_ai import GoogleAIError, generate_content, generate_text


@patch("data.google_ai.litellm.completion")
def test_generate_text_success(mock_completion):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "AI generated text."
    mock_completion.return_value = mock_response

    result = generate_text("Tell me a joke")

    assert result == "AI generated text."
    mock_completion.assert_called_once()
    kwargs = mock_completion.call_args[1]
    assert kwargs["messages"][0]["content"] == "Tell me a joke"
    assert kwargs["model"] == "gemini/gemini-3.1-flash-lite"


def test_generate_text_empty_prompt():
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        generate_text("")


@patch("data.google_ai.litellm.completion")
def test_generate_text_litellm_error(mock_completion):
    mock_completion.side_effect = Exception("LiteLLM Error")

    with pytest.raises(
        GoogleAIError, match="Error when calling litellm: LiteLLM Error"
    ):
        generate_text("test")


@patch("data.google_ai.generate_text")
def test_generate_content(mock_generate_text):
    mock_generate_text.return_value = "Content generated"

    response = generate_content(contents="Test prompt")

    assert response.text == "Content generated"
    mock_generate_text.assert_called_once_with(
        prompt="Test prompt", model="gemini-3.1-flash-lite"
    )
