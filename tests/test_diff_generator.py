"""Tests for diff generator module."""

import pytest

from src.analysis.clause_analyzer import ClauseAnalysis
from src.comparison.aligner import ClauseAlignment
from src.comparison.diff_generator import ComparisonReport, DiffGenerator
from src.parsing.clause_segmenter import Clause


@pytest.fixture()
def generator() -> DiffGenerator:
    """Create a DiffGenerator instance."""
    return DiffGenerator()


def _make_clause(id_: str, text: str) -> Clause:
    """Helper to create test clauses."""
    return Clause(id=id_, text=text, section_type="general", position=0)


def _make_analysis(risk_level: str = "low") -> ClauseAnalysis:
    """Helper to create test clause analysis."""
    return ClauseAnalysis(
        clause_id="1",
        clause_text="text",
        clause_type="payment",
        risk_level=risk_level,
        risk_reasoning="reason",
        key_terms=[],
        summary="summary",
    )


def test_generate_report(generator: DiffGenerator) -> None:
    """Test generating a basic comparison report."""
    ca = _make_clause("1", "Payment in 30 days")
    cb = _make_clause("1", "Payment in 60 days")
    alignments = [ClauseAlignment(ca, cb, 0.85, "modified")]

    report = generator.generate(alignments)

    assert isinstance(report, ComparisonReport)
    assert report.summary["modified"] == 1
    assert report.summary["matched"] == 0
    assert "Contract Comparison Report" in report.markdown


def test_generate_with_risk_comparison(generator: DiffGenerator) -> None:
    """Test report with risk comparison data."""
    alignments = [
        ClauseAlignment(_make_clause("1", "a"), _make_clause("1", "a"), 1.0, "matched")
    ]
    analyses_a = [_make_analysis("high"), _make_analysis("low")]
    analyses_b = [_make_analysis("medium")]

    report = generator.generate(alignments, analyses_a, analyses_b)

    assert "contract_a" in report.risk_comparison
    assert report.risk_comparison["contract_a"]["high"] == 1
    assert report.risk_comparison["contract_b"]["medium"] == 1


def test_generate_no_risk_comparison(generator: DiffGenerator) -> None:
    """Test report without risk comparison."""
    report = generator.generate([])
    assert report.risk_comparison == {}


def test_summary_counts(generator: DiffGenerator) -> None:
    """Test that summary correctly counts each match type."""
    alignments = [
        ClauseAlignment(_make_clause("1", "a"), _make_clause("1", "a"), 1.0, "matched"),
        ClauseAlignment(
            _make_clause("2", "b"), _make_clause("2", "c"), 0.8, "modified"
        ),
        ClauseAlignment(_make_clause("3", "d"), None, 0, "removed"),
        ClauseAlignment(None, _make_clause("4", "e"), 0, "added"),
    ]

    report = generator.generate(alignments)

    assert report.summary["matched"] == 1
    assert report.summary["modified"] == 1
    assert report.summary["removed"] == 1
    assert report.summary["added"] == 1


def test_markdown_contains_modified_details(generator: DiffGenerator) -> None:
    """Test that markdown includes details for modified clauses."""
    ca = _make_clause("1", "Original text here")
    cb = _make_clause("1", "Modified text here")
    alignments = [ClauseAlignment(ca, cb, 0.75, "modified")]

    report = generator.generate(alignments)

    assert "Modified: Clause 1" in report.markdown
    assert "Contract A:" in report.markdown
    assert "Contract B:" in report.markdown


def test_markdown_risk_table(generator: DiffGenerator) -> None:
    """Test that markdown includes risk comparison table."""
    alignments: list[ClauseAlignment] = []
    analyses_a = [_make_analysis("high")]
    analyses_b = [_make_analysis("low")]

    report = generator.generate(alignments, analyses_a, analyses_b)

    assert "Risk Comparison" in report.markdown
    assert "Contract A" in report.markdown


def test_risk_summary(generator: DiffGenerator) -> None:
    """Test risk summary computation."""
    analyses = [
        _make_analysis("high"),
        _make_analysis("high"),
        _make_analysis("medium"),
        _make_analysis("low"),
    ]
    summary = generator._risk_summary(analyses)
    assert summary["high"] == 2
    assert summary["medium"] == 1
    assert summary["low"] == 1


def test_comparison_report_dataclass() -> None:
    """Test ComparisonReport dataclass."""
    report = ComparisonReport(
        summary={"matched": 1},
        alignments=[],
        risk_comparison={},
        markdown="# Report",
    )
    assert report.summary["matched"] == 1
    assert report.markdown == "# Report"
