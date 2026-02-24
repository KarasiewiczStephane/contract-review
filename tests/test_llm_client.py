"""Tests for LLM client abstraction."""

from unittest.mock import MagicMock, patch

import pytest

from src.analysis.llm_client import AnthropicClient, LLMClient, OpenAIClient


def test_llm_client_is_abstract() -> None:
    """Test that LLMClient cannot be instantiated directly."""
    with pytest.raises(TypeError):
        LLMClient()


@patch("openai.OpenAI")
def test_openai_client_complete(mock_openai_cls: MagicMock) -> None:
    """Test OpenAI client complete method."""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response

    client = OpenAIClient(api_key="test-key", model="gpt-4")
    result = client.complete("Hello", system="Be helpful")

    assert result == "Test response"
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4"
    assert len(call_kwargs["messages"]) == 2


@patch("openai.OpenAI")
def test_openai_client_no_system(mock_openai_cls: MagicMock) -> None:
    """Test OpenAI client without system prompt."""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response

    client = OpenAIClient(api_key="test-key")
    client.complete("Hello")

    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"


@patch("anthropic.Anthropic")
def test_anthropic_client_complete(mock_anthropic_cls: MagicMock) -> None:
    """Test Anthropic client complete method."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Anthropic response"
    mock_client.messages.create.return_value = mock_response

    client = AnthropicClient(api_key="test-key", model="claude-3-opus-20240229")
    result = client.complete("Hello", system="Be helpful")

    assert result == "Anthropic response"
    mock_client.messages.create.assert_called_once()


@patch("openai.OpenAI")
def test_openai_client_attributes(mock_openai_cls: MagicMock) -> None:
    """Test OpenAI client attributes are set correctly."""
    client = OpenAIClient(api_key="key", model="gpt-3.5-turbo", temperature=0.5)
    assert client.model == "gpt-3.5-turbo"
    assert client.temperature == 0.5
    assert client.provider == "openai"


@patch("anthropic.Anthropic")
def test_anthropic_client_attributes(mock_anthropic_cls: MagicMock) -> None:
    """Test Anthropic client attributes are set correctly."""
    client = AnthropicClient(api_key="key", model="claude-3-sonnet", temperature=0.3)
    assert client.model == "claude-3-sonnet"
    assert client.temperature == 0.3
    assert client.provider == "anthropic"
