"""Tests for clause alignment module."""

import pytest

from src.comparison.aligner import ClauseAligner, ClauseAlignment
from src.parsing.clause_segmenter import Clause


@pytest.fixture()
def aligner() -> ClauseAligner:
    """Create a ClauseAligner with default threshold."""
    return ClauseAligner(similarity_threshold=0.6)


def _make_clause(id_: str, text: str) -> Clause:
    """Helper to create test clauses."""
    return Clause(id=id_, text=text, section_type="general", position=0)


def test_align_identical_clauses(aligner: ClauseAligner) -> None:
    """Test alignment of identical clauses results in 'matched'."""
    clauses_a = [_make_clause("1", "Payment is due within 30 days.")]
    clauses_b = [_make_clause("1", "Payment is due within 30 days.")]
    result = aligner.align(clauses_a, clauses_b)
    assert len(result) == 1
    assert result[0].match_type == "matched"
    assert result[0].similarity > 0.95


def test_align_similar_clauses(aligner: ClauseAligner) -> None:
    """Test alignment of similar clauses results in 'modified'."""
    clauses_a = [
        _make_clause(
            "1",
            "Payment shall be made within 30 days of the invoice date "
            "by wire transfer to the designated account.",
        )
    ]
    clauses_b = [
        _make_clause(
            "1",
            "Payment shall be made within 60 days of the invoice date "
            "by check to the designated bank account number.",
        )
    ]
    result = aligner.align(clauses_a, clauses_b)
    assert len(result) == 1
    assert result[0].match_type == "modified"
    assert 0.6 <= result[0].similarity <= 0.95


def test_align_removed_clause(aligner: ClauseAligner) -> None:
    """Test that clauses only in A are marked as 'removed'."""
    clauses_a = [_make_clause("1", "This clause is unique to contract A.")]
    clauses_b: list[Clause] = []
    result = aligner.align(clauses_a, clauses_b)
    assert len(result) == 1
    assert result[0].match_type == "removed"
    assert result[0].clause_b is None


def test_align_added_clause(aligner: ClauseAligner) -> None:
    """Test that clauses only in B are marked as 'added'."""
    clauses_a: list[Clause] = []
    clauses_b = [_make_clause("1", "This clause is new in contract B.")]
    result = aligner.align(clauses_a, clauses_b)
    assert len(result) == 1
    assert result[0].match_type == "added"
    assert result[0].clause_a is None


def test_align_mixed(aligner: ClauseAligner) -> None:
    """Test alignment with matched, modified, and unique clauses."""
    clauses_a = [
        _make_clause("1", "Payment is due within 30 days."),
        _make_clause("2", "This contract may be terminated by either party."),
        _make_clause("3", "Only in contract A, completely different text."),
    ]
    clauses_b = [
        _make_clause("1", "Payment is due within 30 days."),
        _make_clause("2", "This agreement may be terminated by either side."),
        _make_clause("4", "New clause only in contract B."),
    ]
    result = aligner.align(clauses_a, clauses_b)
    types = [a.match_type for a in result]
    assert "matched" in types
    assert "added" in types or "removed" in types


def test_align_empty_inputs(aligner: ClauseAligner) -> None:
    """Test alignment with empty inputs returns empty list."""
    result = aligner.align([], [])
    assert result == []


def test_similarity_method(aligner: ClauseAligner) -> None:
    """Test the similarity computation method."""
    sim = aligner._similarity("hello world", "hello world")
    assert sim == 1.0

    sim = aligner._similarity("hello world", "goodbye world")
    assert 0 < sim < 1


def test_custom_threshold() -> None:
    """Test that custom threshold affects matching."""
    strict_aligner = ClauseAligner(similarity_threshold=0.99)
    clauses_a = [
        _make_clause("1", "The vendor shall deliver goods within 30 business days.")
    ]
    clauses_b = [
        _make_clause(
            "1",
            "The supplier must ship all products within 90 calendar days after order.",
        )
    ]
    result = strict_aligner.align(clauses_a, clauses_b)
    assert result[0].match_type in ("modified", "removed")


def test_clause_alignment_dataclass() -> None:
    """Test ClauseAlignment dataclass."""
    c = _make_clause("1", "test")
    alignment = ClauseAlignment(
        clause_a=c, clause_b=c, similarity=1.0, match_type="matched"
    )
    assert alignment.similarity == 1.0
    assert alignment.match_type == "matched"
