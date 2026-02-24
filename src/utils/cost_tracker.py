"""Cost tracking for LLM API usage.

Tracks token usage and estimates costs across different
LLM providers and models.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

import tiktoken

from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class UsageRecord:
    """A single LLM API usage record."""

    timestamp: datetime
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float


class CostTracker:
    """Tracks LLM API token usage and costs.

    Maintains a running log of API calls with token counts
    and estimated costs based on known model pricing.
    """

    PRICING: dict[str, dict[str, float]] = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }

    def __init__(self) -> None:
        self.records: list[UsageRecord] = []
        self._encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string.

        Args:
            text: Input text to tokenize.

        Returns:
            Number of tokens.
        """
        return len(self._encoder.encode(text))

    def track(
        self,
        provider: str,
        model: str,
        input_text: str,
        output_text: str,
    ) -> None:
        """Record an API call with token and cost tracking.

        Args:
            provider: LLM provider name (openai, anthropic).
            model: Model identifier.
            input_text: The input/prompt text.
            output_text: The response text.
        """
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        self.records.append(
            UsageRecord(
                timestamp=datetime.now(),
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
            )
        )
        logger.info(
            "Tracked %s/%s: %d in, %d out, $%.4f",
            provider,
            model,
            input_tokens,
            output_tokens,
            cost,
        )

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate estimated cost for a given model and token counts.

        Args:
            model: Model identifier.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        pricing = None
        for key in self.PRICING:
            if key in model.lower():
                pricing = self.PRICING[key]
                break
        if not pricing:
            return 0.0

        return (
            input_tokens / 1000 * pricing["input"]
            + output_tokens / 1000 * pricing["output"]
        )

    def total_cost(self) -> float:
        """Get the total accumulated cost.

        Returns:
            Total cost in USD.
        """
        return sum(r.cost for r in self.records)

    def total_tokens(self) -> dict[str, int]:
        """Get total input and output token counts.

        Returns:
            Dictionary with 'input' and 'output' token totals.
        """
        return {
            "input": sum(r.input_tokens for r in self.records),
            "output": sum(r.output_tokens for r in self.records),
        }

    def summary(self) -> dict[str, object]:
        """Get a summary of all tracked usage.

        Returns:
            Dictionary with total_cost, total_tokens, and num_requests.
        """
        return {
            "total_cost": f"${self.total_cost():.4f}",
            "total_tokens": self.total_tokens(),
            "num_requests": len(self.records),
        }
