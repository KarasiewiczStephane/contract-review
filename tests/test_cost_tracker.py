"""Tests for cost tracking utility."""

import pytest

from src.utils.cost_tracker import CostTracker, UsageRecord


@pytest.fixture()
def tracker() -> CostTracker:
    """Create a fresh CostTracker instance."""
    return CostTracker()


def test_count_tokens(tracker: CostTracker) -> None:
    """Test token counting."""
    count = tracker.count_tokens("Hello, world!")
    assert count > 0
    assert isinstance(count, int)


def test_count_tokens_empty(tracker: CostTracker) -> None:
    """Test token counting for empty string."""
    count = tracker.count_tokens("")
    assert count == 0


def test_track_openai(tracker: CostTracker) -> None:
    """Test tracking an OpenAI API call."""
    tracker.track("openai", "gpt-4", "What is a contract?", "A contract is...")
    assert len(tracker.records) == 1
    assert tracker.records[0].provider == "openai"
    assert tracker.records[0].model == "gpt-4"
    assert tracker.records[0].input_tokens > 0
    assert tracker.records[0].output_tokens > 0
    assert tracker.records[0].cost > 0


def test_track_anthropic(tracker: CostTracker) -> None:
    """Test tracking an Anthropic API call."""
    tracker.track("anthropic", "claude-3-opus", "Analyze this", "Analysis result")
    assert len(tracker.records) == 1
    assert tracker.records[0].provider == "anthropic"
    assert tracker.records[0].cost > 0


def test_track_unknown_model(tracker: CostTracker) -> None:
    """Test tracking with an unknown model returns zero cost."""
    tracker.track("custom", "unknown-model", "input", "output")
    assert tracker.records[0].cost == 0.0


def test_total_cost(tracker: CostTracker) -> None:
    """Test total cost calculation across multiple calls."""
    tracker.track("openai", "gpt-4", "Hello", "World")
    tracker.track("openai", "gpt-4", "More input", "More output")
    assert tracker.total_cost() > 0


def test_total_cost_empty(tracker: CostTracker) -> None:
    """Test total cost with no records."""
    assert tracker.total_cost() == 0.0


def test_total_tokens(tracker: CostTracker) -> None:
    """Test total token counting."""
    tracker.track("openai", "gpt-4", "Input text here", "Output text here")
    tokens = tracker.total_tokens()
    assert tokens["input"] > 0
    assert tokens["output"] > 0


def test_total_tokens_empty(tracker: CostTracker) -> None:
    """Test total tokens with no records."""
    tokens = tracker.total_tokens()
    assert tokens["input"] == 0
    assert tokens["output"] == 0


def test_summary(tracker: CostTracker) -> None:
    """Test summary generation."""
    tracker.track("openai", "gpt-4", "Test input", "Test output")
    summary = tracker.summary()
    assert "total_cost" in summary
    assert "total_tokens" in summary
    assert "num_requests" in summary
    assert summary["num_requests"] == 1
    assert summary["total_cost"].startswith("$")


def test_summary_empty(tracker: CostTracker) -> None:
    """Test summary with no records."""
    summary = tracker.summary()
    assert summary["num_requests"] == 0
    assert summary["total_cost"] == "$0.0000"


def test_multiple_providers(tracker: CostTracker) -> None:
    """Test tracking across multiple providers."""
    tracker.track("openai", "gpt-4", "Hello", "World")
    tracker.track("anthropic", "claude-3-sonnet", "Hello", "World")
    assert len(tracker.records) == 2
    assert tracker.total_cost() > 0


def test_gpt35_pricing(tracker: CostTracker) -> None:
    """Test GPT-3.5-turbo pricing is cheaper than GPT-4."""
    tracker_35 = CostTracker()
    tracker_4 = CostTracker()
    text = "This is a test input for pricing comparison."
    tracker_35.track("openai", "gpt-3.5-turbo", text, text)
    tracker_4.track("openai", "gpt-4", text, text)
    assert tracker_35.total_cost() < tracker_4.total_cost()


def test_usage_record_dataclass() -> None:
    """Test UsageRecord dataclass."""
    from datetime import datetime

    record = UsageRecord(
        timestamp=datetime.now(),
        provider="openai",
        model="gpt-4",
        input_tokens=100,
        output_tokens=50,
        cost=0.006,
    )
    assert record.provider == "openai"
    assert record.input_tokens == 100
