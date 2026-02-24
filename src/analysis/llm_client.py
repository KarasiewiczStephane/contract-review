"""LLM client abstraction for OpenAI and Anthropic APIs.

Provides a unified interface for interacting with different LLM providers.
"""

import logging
from abc import ABC, abstractmethod

from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt to the LLM and return the response.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The LLM's text response.
        """


class OpenAIClient(LLMClient):
    """OpenAI API client.

    Args:
        api_key: OpenAI API key.
        model: Model identifier.
        temperature: Sampling temperature.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.0,
    ) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.provider = "openai"

    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt to OpenAI and return the response.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The model's text response.
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        logger.info("Sending request to OpenAI model %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic API client.

    Args:
        api_key: Anthropic API key.
        model: Model identifier.
        temperature: Sampling temperature.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.0,
    ) -> None:
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.provider = "anthropic"

    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt to Anthropic and return the response.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The model's text response.
        """
        logger.info("Sending request to Anthropic model %s", self.model)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
