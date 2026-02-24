"""Tests for metadata extraction module."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from src.parsing.metadata_extractor import ContractMetadata, MetadataExtractor


@pytest.fixture()
def mock_nlp() -> MagicMock:
    """Create a mock spaCy NLP model."""
    nlp = MagicMock()
    doc = MagicMock()
    entity = MagicMock()
    entity.label_ = "ORG"
    entity.text = "Acme Corp"
    doc.ents = [entity]
    nlp.return_value = doc
    return nlp


@pytest.fixture()
def extractor(mock_nlp: MagicMock) -> MetadataExtractor:
    """Create a MetadataExtractor with mocked NLP."""
    return MetadataExtractor(nlp=mock_nlp)


@pytest.fixture()
def extractor_no_nlp() -> MetadataExtractor:
    """Create a MetadataExtractor without NLP."""
    return MetadataExtractor(nlp=None)


def test_extract_parties_with_nlp(extractor: MetadataExtractor) -> None:
    """Test party extraction using NLP entities."""
    text = "Agreement between Acme Corp and Widget Inc."
    metadata = extractor.extract(text)
    assert "Acme Corp" in metadata.parties


def test_extract_parties_between_pattern(extractor_no_nlp: MetadataExtractor) -> None:
    """Test party extraction using 'between X and Y' pattern."""
    text = "This agreement is between Alpha LLC and Beta Inc."
    metadata = extractor_no_nlp.extract(text)
    assert "Alpha LLC" in metadata.parties
    assert "Beta Inc" in metadata.parties


def test_extract_effective_date(extractor_no_nlp: MetadataExtractor) -> None:
    """Test extraction of effective date."""
    text = "This agreement is effective January 15, 2024."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.effective_date == date(2024, 1, 15)


def test_extract_date_numeric_format(extractor_no_nlp: MetadataExtractor) -> None:
    """Test extraction of date in numeric format."""
    text = "Dated 01/15/2024 for reference."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.effective_date == date(2024, 1, 15)


def test_extract_no_date(extractor_no_nlp: MetadataExtractor) -> None:
    """Test that missing date returns None."""
    text = "This is a contract with no dates mentioned."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.effective_date is None


def test_extract_governing_law(extractor_no_nlp: MetadataExtractor) -> None:
    """Test governing law extraction."""
    text = "This agreement shall be governed by the laws of California."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.governing_law == "California"


def test_extract_governing_law_construed(extractor_no_nlp: MetadataExtractor) -> None:
    """Test governing law with 'construed under' phrasing."""
    text = "Construed in accordance with the laws of New York."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.governing_law == "New York"


def test_extract_no_governing_law(extractor_no_nlp: MetadataExtractor) -> None:
    """Test that missing governing law returns None."""
    text = "This is a simple contract."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.governing_law is None


def test_detect_nda(extractor_no_nlp: MetadataExtractor) -> None:
    """Test NDA contract type detection."""
    text = "NON-DISCLOSURE AGREEMENT. This confidentiality agreement..."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type == "nda"


def test_detect_employment(extractor_no_nlp: MetadataExtractor) -> None:
    """Test employment contract type detection."""
    text = "EMPLOYMENT AGREEMENT. The employer agrees..."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type == "employment"


def test_detect_service(extractor_no_nlp: MetadataExtractor) -> None:
    """Test service agreement type detection."""
    text = "MASTER SERVICE AGREEMENT. The provider shall..."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type == "service"


def test_detect_license(extractor_no_nlp: MetadataExtractor) -> None:
    """Test license agreement type detection."""
    text = "SOFTWARE LICENSE AGREEMENT. The licensor grants..."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type == "license"


def test_detect_lease(extractor_no_nlp: MetadataExtractor) -> None:
    """Test lease agreement type detection."""
    text = "LEASE AGREEMENT. The landlord agrees..."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type == "lease"


def test_detect_unknown_type(extractor_no_nlp: MetadataExtractor) -> None:
    """Test that unknown contract type returns None."""
    text = "This is some generic legal document."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.contract_type is None


def test_expiration_date_always_none(extractor_no_nlp: MetadataExtractor) -> None:
    """Test that expiration_date is None (not yet implemented)."""
    text = "Some contract text."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.expiration_date is None


def test_contract_metadata_dataclass() -> None:
    """Test ContractMetadata dataclass."""
    meta = ContractMetadata(
        parties=["A", "B"],
        effective_date=date(2024, 1, 1),
        governing_law="Texas",
        contract_type="nda",
        expiration_date=None,
    )
    assert meta.parties == ["A", "B"]
    assert meta.governing_law == "Texas"


def test_extract_date_invalid_parse(extractor_no_nlp: MetadataExtractor) -> None:
    """Test that an invalid date match is handled gracefully."""
    text = "Effective Notamonth 99, 9999 this contract begins."
    metadata = extractor_no_nlp.extract(text)
    assert metadata.effective_date is None


def test_parties_deduplication(mock_nlp: MagicMock) -> None:
    """Test that duplicate parties are removed."""
    entity1 = MagicMock()
    entity1.label_ = "ORG"
    entity1.text = "Acme Corp"
    entity2 = MagicMock()
    entity2.label_ = "ORG"
    entity2.text = "Acme Corp"
    doc = MagicMock()
    doc.ents = [entity1, entity2]
    mock_nlp.return_value = doc

    extractor = MetadataExtractor(nlp=mock_nlp)
    text = "Agreement between Acme Corp and Widget Inc."
    metadata = extractor.extract(text)
    acme_count = metadata.parties.count("Acme Corp")
    assert acme_count == 1


def test_parties_max_five() -> None:
    """Test that parties list is limited to 5."""
    nlp = MagicMock()
    entities = []
    for i in range(10):
        e = MagicMock()
        e.label_ = "ORG"
        e.text = f"Company {i}"
        entities.append(e)
    doc = MagicMock()
    doc.ents = entities
    nlp.return_value = doc

    extractor = MetadataExtractor(nlp=nlp)
    metadata = extractor.extract("Some text")
    assert len(metadata.parties) <= 5
