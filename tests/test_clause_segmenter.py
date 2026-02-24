"""Tests for clause segmentation module."""

import pytest

from src.parsing.clause_segmenter import Clause, ClauseSegmenter


@pytest.fixture()
def segmenter() -> ClauseSegmenter:
    """Create a ClauseSegmenter instance."""
    return ClauseSegmenter()


def test_segment_numbered_clauses(segmenter: ClauseSegmenter) -> None:
    """Test segmenting text with numbered clauses."""
    text = "1. First clause content.\n2. Second clause content.\n3. Third clause."
    clauses = segmenter.segment(text)
    assert len(clauses) >= 2
    assert all(isinstance(c, Clause) for c in clauses)


def test_segment_lettered_clauses(segmenter: ClauseSegmenter) -> None:
    """Test segmenting text with lettered sub-clauses."""
    text = "a) First item.\nb) Second item.\nc) Third item."
    clauses = segmenter.segment(text)
    assert len(clauses) >= 2


def test_segment_no_pattern_returns_single(segmenter: ClauseSegmenter) -> None:
    """Test that text with no patterns returns a single clause."""
    text = "This is just a paragraph of text without numbering."
    clauses = segmenter.segment(text)
    assert len(clauses) == 1
    assert clauses[0].id == "1"
    assert clauses[0].text == text


def test_segment_empty_text(segmenter: ClauseSegmenter) -> None:
    """Test segmenting empty text returns empty list."""
    clauses = segmenter.segment("")
    assert clauses == []


def test_segment_preserves_section_type(segmenter: ClauseSegmenter) -> None:
    """Test that section_type is passed through to clauses."""
    text = "1. Some clause."
    clauses = segmenter.segment(text, section_type="payment")
    assert all(c.section_type == "payment" for c in clauses)


def test_segment_positions_are_sequential(segmenter: ClauseSegmenter) -> None:
    """Test that clause positions are sequential."""
    text = "1. First.\n2. Second.\n3. Third."
    clauses = segmenter.segment(text)
    positions = [c.position for c in clauses]
    assert positions == sorted(positions)


def test_segment_hierarchical_numbering(segmenter: ClauseSegmenter) -> None:
    """Test segmenting with hierarchical numbering like 1.1, 1.2."""
    text = "1.1 Sub-clause one.\n1.2 Sub-clause two."
    clauses = segmenter.segment(text)
    assert len(clauses) >= 1


def test_segment_strips_whitespace(segmenter: ClauseSegmenter) -> None:
    """Test that clause text is stripped of extra whitespace."""
    text = "1.  Some clause with spaces.  "
    clauses = segmenter.segment(text)
    for clause in clauses:
        assert clause.text == clause.text.strip()


def test_clause_dataclass() -> None:
    """Test Clause dataclass instantiation."""
    clause = Clause(id="1.1", text="Test text", section_type="payment", position=0)
    assert clause.id == "1.1"
    assert clause.text == "Test text"
    assert clause.section_type == "payment"
    assert clause.position == 0


def test_default_section_type(segmenter: ClauseSegmenter) -> None:
    """Test default section_type is 'unknown'."""
    text = "Some paragraph text."
    clauses = segmenter.segment(text)
    assert clauses[0].section_type == "unknown"
