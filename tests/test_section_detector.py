"""Tests for section detection module."""

import pytest

from src.parsing.section_detector import Section, SectionDetector, SectionType


@pytest.fixture()
def detector() -> SectionDetector:
    """Create a SectionDetector instance."""
    return SectionDetector()


def test_detect_definitions_section(detector: SectionDetector) -> None:
    """Test detecting a definitions section."""
    text = "Preamble text\nSection 1. Definitions\nTerm means something."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.DEFINITIONS for s in sections)


def test_detect_termination_section(detector: SectionDetector) -> None:
    """Test detecting a termination section."""
    text = "Some text\nArticle 5. Termination\nEither party may terminate."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.TERMINATION for s in sections)


def test_detect_payment_section(detector: SectionDetector) -> None:
    """Test detecting a payment section."""
    text = "Intro\nSection 3. Payment\nPayment terms here."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.PAYMENT for s in sections)


def test_detect_confidentiality_section(detector: SectionDetector) -> None:
    """Test detecting a confidentiality section."""
    text = "Intro\nConfidentiality\nAll information is confidential."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.CONFIDENTIALITY for s in sections)


def test_detect_liability_section(detector: SectionDetector) -> None:
    """Test detecting a liability section."""
    text = "Intro\nLimitation of Liability\nNeither party shall be liable."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.LIABILITY for s in sections)


def test_detect_indemnification_section(detector: SectionDetector) -> None:
    """Test detecting an indemnification section."""
    text = "Intro\nIndemnification\nEach party shall indemnify."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.INDEMNIFICATION for s in sections)


def test_detect_dispute_resolution(detector: SectionDetector) -> None:
    """Test detecting a dispute resolution section."""
    text = "Intro\nDispute Resolution\nAny dispute shall be resolved."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.DISPUTE_RESOLUTION for s in sections)


def test_detect_obligations_section(detector: SectionDetector) -> None:
    """Test detecting an obligations section."""
    text = "Intro\nObligations\nThe parties shall perform."
    sections = detector.detect_sections(text)
    assert any(s.section_type == SectionType.OBLIGATIONS for s in sections)


def test_no_sections_returns_unknown(detector: SectionDetector) -> None:
    """Test that text with no recognizable sections returns UNKNOWN."""
    text = "This is just plain text without any sections."
    sections = detector.detect_sections(text)
    assert len(sections) == 1
    assert sections[0].section_type == SectionType.UNKNOWN


def test_multiple_sections(detector: SectionDetector) -> None:
    """Test detecting multiple sections in a document."""
    text = (
        "Preamble\n"
        "Section 1. Definitions\n"
        "Term A means something.\n"
        "Section 2. Payment\n"
        "Payment is due monthly.\n"
        "Section 3. Termination\n"
        "Either party may terminate."
    )
    sections = detector.detect_sections(text)
    types = [s.section_type for s in sections]
    assert SectionType.DEFINITIONS in types
    assert SectionType.PAYMENT in types
    assert SectionType.TERMINATION in types


def test_section_content_preserved(detector: SectionDetector) -> None:
    """Test that section content is captured correctly."""
    text = (
        "Section 1. Definitions\nTerm A means something.\nTerm B means another thing."
    )
    sections = detector.detect_sections(text)
    assert len(sections) == 1
    assert "Term A means something" in sections[0].content
    assert "Term B means another thing" in sections[0].content


def test_section_line_numbers(detector: SectionDetector) -> None:
    """Test that section start/end lines are tracked."""
    text = "Preamble\nDefinitions\nSome terms."
    sections = detector.detect_sections(text)
    for section in sections:
        assert section.start_line >= 0
        assert section.end_line >= section.start_line


def test_classify_line_returns_none(detector: SectionDetector) -> None:
    """Test that non-section lines return None."""
    result = detector._classify_line("This is regular text")
    assert result is None


def test_section_type_enum_values() -> None:
    """Test SectionType enum values."""
    assert SectionType.PREAMBLE.value == "preamble"
    assert SectionType.DEFINITIONS.value == "definitions"
    assert SectionType.UNKNOWN.value == "unknown"


def test_section_dataclass() -> None:
    """Test Section dataclass instantiation."""
    section = Section(
        section_type=SectionType.PAYMENT,
        title="Payment Terms",
        content="Pay within 30 days.",
        start_line=5,
        end_line=10,
    )
    assert section.title == "Payment Terms"
    assert section.start_line == 5
