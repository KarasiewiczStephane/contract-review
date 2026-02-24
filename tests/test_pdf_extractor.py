"""Tests for PDF text extraction module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.parsing.pdf_extractor import ExtractedDocument, PageContent, PDFExtractor


@pytest.fixture()
def extractor() -> PDFExtractor:
    """Create a PDFExtractor instance with default settings."""
    return PDFExtractor(max_pages=10)


@pytest.fixture()
def mock_pdf_page() -> MagicMock:
    """Create a mock pdfplumber page."""
    page = MagicMock()
    page.extract_text.return_value = "This is test content."
    page.extract_tables.return_value = []
    return page


def test_extract_file_not_found(extractor: PDFExtractor) -> None:
    """Test that extracting a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="PDF not found"):
        extractor.extract("/nonexistent/file.pdf")


def test_extract_streaming_file_not_found(extractor: PDFExtractor) -> None:
    """Test that streaming extraction of nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="PDF not found"):
        list(extractor.extract_streaming("/nonexistent/file.pdf"))


@patch("src.parsing.pdf_extractor.pdfplumber")
def test_extract_success(mock_pdfplumber: MagicMock, tmp_path: Path) -> None:
    """Test successful PDF extraction."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Contract agreement text."
    mock_page.extract_tables.return_value = [[["Header1", "Header2"], ["Val1", "Val2"]]]

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdfplumber.open.return_value = mock_pdf

    extractor = PDFExtractor(max_pages=50)
    doc = extractor.extract(pdf_path)

    assert isinstance(doc, ExtractedDocument)
    assert doc.filename == "test.pdf"
    assert doc.total_pages == 1
    assert len(doc.pages) == 1
    assert doc.pages[0].text == "Contract agreement text."
    assert doc.full_text == "Contract agreement text."
    assert len(doc.pages[0].tables) == 1


@patch("src.parsing.pdf_extractor.pdfplumber")
def test_extract_exceeds_max_pages(mock_pdfplumber: MagicMock, tmp_path: Path) -> None:
    """Test that exceeding max_pages raises ValueError."""
    pdf_path = tmp_path / "big.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    mock_pdf = MagicMock()
    mock_pdf.pages = [MagicMock() for _ in range(15)]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdfplumber.open.return_value = mock_pdf

    extractor = PDFExtractor(max_pages=10)
    with pytest.raises(ValueError, match="exceeds limit of 10"):
        extractor.extract(pdf_path)


@patch("src.parsing.pdf_extractor.pdfplumber")
def test_extract_empty_page(mock_pdfplumber: MagicMock, tmp_path: Path) -> None:
    """Test extraction of a page with no text."""
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_page.extract_tables.return_value = None

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdfplumber.open.return_value = mock_pdf

    extractor = PDFExtractor()
    doc = extractor.extract(pdf_path)

    assert doc.pages[0].text == ""
    assert doc.pages[0].tables == []


@patch("src.parsing.pdf_extractor.pdfplumber")
def test_extract_streaming(mock_pdfplumber: MagicMock, tmp_path: Path) -> None:
    """Test streaming extraction yields pages one by one."""
    pdf_path = tmp_path / "stream.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    pages = []
    for i in range(3):
        p = MagicMock()
        p.extract_text.return_value = f"Page {i + 1} text"
        p.extract_tables.return_value = []
        pages.append(p)

    mock_pdf = MagicMock()
    mock_pdf.pages = pages
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdfplumber.open.return_value = mock_pdf

    extractor = PDFExtractor(max_pages=50)
    results = list(extractor.extract_streaming(pdf_path))

    assert len(results) == 3
    assert all(isinstance(r, PageContent) for r in results)
    assert results[0].text == "Page 1 text"
    assert results[2].page_number == 3


@patch("src.parsing.pdf_extractor.pdfplumber")
def test_extract_multiple_pages(mock_pdfplumber: MagicMock, tmp_path: Path) -> None:
    """Test extraction of multi-page PDF joins text correctly."""
    pdf_path = tmp_path / "multi.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    pages = []
    for i in range(3):
        p = MagicMock()
        p.extract_text.return_value = f"Section {i + 1}"
        p.extract_tables.return_value = []
        pages.append(p)

    mock_pdf = MagicMock()
    mock_pdf.pages = pages
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdfplumber.open.return_value = mock_pdf

    extractor = PDFExtractor()
    doc = extractor.extract(pdf_path)

    assert doc.total_pages == 3
    assert "Section 1" in doc.full_text
    assert "Section 3" in doc.full_text


def test_page_content_dataclass() -> None:
    """Test PageContent dataclass."""
    page = PageContent(page_number=1, text="hello", tables=[])
    assert page.page_number == 1
    assert page.text == "hello"


def test_extracted_document_dataclass() -> None:
    """Test ExtractedDocument dataclass."""
    doc = ExtractedDocument(filename="test.pdf", total_pages=0, pages=[], full_text="")
    assert doc.filename == "test.pdf"
    assert doc.total_pages == 0
