"""Tests for risk scorer module."""

import pytest

from src.analysis.clause_analyzer import ClauseAnalysis
from src.analysis.risk_scorer import RiskReport, RiskScorer


@pytest.fixture()
def scorer() -> RiskScorer:
    """Create a RiskScorer instance."""
    return RiskScorer()


def _make_analysis(
    clause_type: str = "payment",
    risk_level: str = "low",
    risk_reasoning: str = "Standard terms",
) -> ClauseAnalysis:
    """Helper to create a ClauseAnalysis for testing."""
    return ClauseAnalysis(
        clause_id="1",
        clause_text="Some clause text",
        clause_type=clause_type,
        risk_level=risk_level,
        risk_reasoning=risk_reasoning,
        key_terms=[],
        summary="Test summary",
    )


def test_score_empty_analyses(scorer: RiskScorer) -> None:
    """Test scoring with no analyses returns default report."""
    report = scorer.score([])
    assert report.overall_score == 50.0
    assert report.risk_level == "medium"
    assert report.high_risk_clauses == []


def test_score_all_low_risk(scorer: RiskScorer) -> None:
    """Test scoring with all low-risk clauses."""
    analyses = [_make_analysis(risk_level="low") for _ in range(3)]
    report = scorer.score(analyses)
    assert report.overall_score < 40
    assert report.risk_level == "low"


def test_score_all_high_risk(scorer: RiskScorer) -> None:
    """Test scoring with all high-risk clauses."""
    analyses = [_make_analysis(risk_level="high") for _ in range(3)]
    report = scorer.score(analyses)
    assert report.overall_score == 100.0
    assert report.risk_level == "high"


def test_score_mixed_risk(scorer: RiskScorer) -> None:
    """Test scoring with mixed risk levels."""
    analyses = [
        _make_analysis(risk_level="low"),
        _make_analysis(risk_level="medium"),
        _make_analysis(risk_level="high"),
    ]
    report = scorer.score(analyses)
    assert 40 <= report.overall_score <= 80
    assert report.risk_level == "medium"


def test_high_risk_clauses_identified(scorer: RiskScorer) -> None:
    """Test that high-risk clauses are listed in report."""
    analyses = [
        _make_analysis(risk_level="high", clause_type="liability"),
        _make_analysis(risk_level="low", clause_type="payment"),
    ]
    report = scorer.score(analyses)
    assert len(report.high_risk_clauses) == 1
    assert report.high_risk_clauses[0].clause_type == "liability"


def test_missing_clauses_detected(scorer: RiskScorer) -> None:
    """Test that missing expected clauses are reported."""
    analyses = [_make_analysis(clause_type="payment")]
    report = scorer.score(analyses)
    assert "liability" in report.missing_clauses
    assert "termination" in report.missing_clauses
    assert "confidentiality" in report.missing_clauses
    assert "dispute_resolution" in report.missing_clauses


def test_no_missing_clauses(scorer: RiskScorer) -> None:
    """Test that present expected clauses are not reported as missing."""
    analyses = [
        _make_analysis(clause_type="liability"),
        _make_analysis(clause_type="termination"),
        _make_analysis(clause_type="confidentiality"),
        _make_analysis(clause_type="dispute_resolution"),
    ]
    report = scorer.score(analyses)
    assert report.missing_clauses == []


def test_recommendations_for_high_risk(scorer: RiskScorer) -> None:
    """Test that recommendations are generated for high-risk clauses."""
    analyses = [
        _make_analysis(
            clause_type="liability",
            risk_level="high",
            risk_reasoning="Unlimited liability",
        )
    ]
    report = scorer.score(analyses)
    assert any("liability" in r for r in report.recommendations)


def test_recommendations_for_missing(scorer: RiskScorer) -> None:
    """Test that recommendations include missing clause suggestions."""
    analyses = [_make_analysis(clause_type="payment")]
    report = scorer.score(analyses)
    assert any("Consider adding" in r for r in report.recommendations)


def test_score_to_level_low(scorer: RiskScorer) -> None:
    """Test low score classification."""
    assert scorer._score_to_level(20.0) == "low"


def test_score_to_level_medium(scorer: RiskScorer) -> None:
    """Test medium score classification."""
    assert scorer._score_to_level(50.0) == "medium"


def test_score_to_level_high(scorer: RiskScorer) -> None:
    """Test high score classification."""
    assert scorer._score_to_level(80.0) == "high"


def test_risk_report_dataclass() -> None:
    """Test RiskReport dataclass."""
    report = RiskReport(
        overall_score=45.0,
        risk_level="medium",
        high_risk_clauses=[],
        missing_clauses=["liability"],
        unusual_terms=[],
        recommendations=["Add liability clause"],
    )
    assert report.overall_score == 45.0
    assert report.risk_level == "medium"
