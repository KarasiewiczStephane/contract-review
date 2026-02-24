"""Tests for clause analyzer module."""

import json
from unittest.mock import MagicMock

import pytest

from src.analysis.clause_analyzer import ClauseAnalysis, ClauseAnalyzer
from src.parsing.clause_segmenter import Clause


@pytest.fixture()
def mock_llm() -> MagicMock:
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.complete.return_value = json.dumps(
        {
            "clause_type": "payment",
            "risk_level": "low",
            "risk_reasoning": "Standard payment terms",
            "key_terms": ["30 days", "net"],
            "summary": "Payment is due within 30 days.",
        }
    )
    return llm


@pytest.fixture()
def analyzer(mock_llm: MagicMock) -> ClauseAnalyzer:
    """Create a ClauseAnalyzer with mocked LLM."""
    return ClauseAnalyzer(llm_client=mock_llm)


@pytest.fixture()
def sample_clause() -> Clause:
    """Create a sample clause for testing."""
    return Clause(
        id="1.1",
        text="Payment shall be due within 30 days of invoice date.",
        section_type="payment",
        position=0,
    )


def test_analyze_clause(analyzer: ClauseAnalyzer, sample_clause: Clause) -> None:
    """Test analyzing a single clause."""
    result = analyzer.analyze(sample_clause)

    assert isinstance(result, ClauseAnalysis)
    assert result.clause_id == "1.1"
    assert result.clause_type == "payment"
    assert result.risk_level == "low"
    assert "30 days" in result.key_terms
    assert result.summary == "Payment is due within 30 days."


def test_analyze_batch(analyzer: ClauseAnalyzer, sample_clause: Clause) -> None:
    """Test batch analysis of multiple clauses."""
    clauses = [sample_clause, sample_clause]
    results = analyzer.analyze_batch(clauses)

    assert len(results) == 2
    assert all(isinstance(r, ClauseAnalysis) for r in results)


def test_analyze_malformed_json(sample_clause: Clause) -> None:
    """Test fallback parsing when LLM returns invalid JSON."""
    llm = MagicMock()
    llm.complete.return_value = "This is not valid JSON at all."

    analyzer = ClauseAnalyzer(llm_client=llm)
    result = analyzer.analyze(sample_clause)

    assert result.clause_type == "other"
    assert result.risk_level == "medium"
    assert "This is not valid JSON" in result.summary


def test_analyze_missing_fields(sample_clause: Clause) -> None:
    """Test handling of partial JSON response."""
    llm = MagicMock()
    llm.complete.return_value = json.dumps({"clause_type": "liability"})

    analyzer = ClauseAnalyzer(llm_client=llm)
    result = analyzer.analyze(sample_clause)

    assert result.clause_type == "liability"
    assert result.risk_level == "medium"
    assert result.key_terms == []
    assert result.summary == ""


def test_clause_analysis_dataclass() -> None:
    """Test ClauseAnalysis dataclass."""
    analysis = ClauseAnalysis(
        clause_id="1",
        clause_text="Some text",
        clause_type="payment",
        risk_level="high",
        risk_reasoning="Unusual terms",
        key_terms=["90 days"],
        summary="Long payment terms.",
    )
    assert analysis.clause_id == "1"
    assert analysis.risk_level == "high"


def test_analyze_empty_batch(analyzer: ClauseAnalyzer) -> None:
    """Test batch analysis with empty list."""
    results = analyzer.analyze_batch([])
    assert results == []


def test_parse_fallback(analyzer: ClauseAnalyzer) -> None:
    """Test the fallback parser directly."""
    result = analyzer._parse_fallback("Some long response text here")
    assert result["clause_type"] == "other"
    assert result["risk_level"] == "medium"
    assert "Some long response" in result["summary"]
