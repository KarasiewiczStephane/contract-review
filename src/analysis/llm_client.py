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


class DemoClient(LLMClient):
    """Demo client that returns simulated LLM responses without API calls."""

    CLAUSE_TYPES = [
        "confidentiality",
        "termination",
        "indemnification",
        "liability",
        "payment",
        "ip_ownership",
        "non_compete",
        "dispute_resolution",
        "force_majeure",
        "renewal",
    ]

    RISK_REASONING = {
        "high": [
            "Unlimited liability exposure with no cap on damages",
            "Non-compete clause is overly broad in scope and duration",
            "Indemnification is one-sided with no mutual obligation",
            "Automatic renewal with no opt-out mechanism",
        ],
        "medium": [
            "Standard termination clause but notice period is short",
            "Confidentiality obligations survive indefinitely",
            "Payment terms favor one party with late penalty clause",
            "IP assignment clause could be interpreted broadly",
        ],
        "low": [
            "Standard mutual confidentiality with reasonable scope",
            "Clear dispute resolution process with arbitration",
            "Force majeure clause covers standard scenarios",
            "Governing law and jurisdiction are clearly defined",
        ],
    }

    def __init__(self) -> None:
        self.provider = "demo"
        self._call_count = 0

    def complete(self, prompt: str, system: str = "") -> str:
        import json as _json
        import hashlib

        text_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
        idx = text_hash % len(self.CLAUSE_TYPES)
        clause_type = self.CLAUSE_TYPES[idx]

        risk_levels = ["low", "medium", "high"]
        risk_level = risk_levels[self._call_count % 3]
        reasoning_list = self.RISK_REASONING[risk_level]
        reasoning = reasoning_list[self._call_count % len(reasoning_list)]
        self._call_count += 1

        result = {
            "clause_type": clause_type,
            "risk_level": risk_level,
            "risk_reasoning": reasoning,
            "key_terms": ["30 days notice", "12 months", "Delaware law"],
            "summary": f"This {clause_type.replace('_', ' ')} clause defines obligations "
            f"between the parties. Risk level: {risk_level}.",
        }
        logger.info("Demo client returning simulated response for %s", clause_type)
        return _json.dumps(result)


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
        model: str = "gpt-4o-mini",
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
        model: str = "claude-sonnet-4-20250514",
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
