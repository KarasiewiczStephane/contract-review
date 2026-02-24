"""PDF text extraction module using pdfplumber.

Extracts text, tables, and metadata from PDF contract documents.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pdfplumber

from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class PageContent:
    """Content extracted from a single PDF page."""

    page_number: int
    text: str
    tables: list[list[list[str]]]


@dataclass
class ExtractedDocument:
    """Complete extracted content from a PDF document."""

    filename: str
    total_pages: int
    pages: list[PageContent]
    full_text: str


class PDFExtractor:
    """Extracts text and tables from PDF documents.

    Args:
        max_pages: Maximum number of pages to process.
    """

    def __init__(self, max_pages: int = 50) -> None:
        self.max_pages = max_pages

    def extract(self, pdf_path: str | Path) -> ExtractedDocument:
        """Extract all content from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            ExtractedDocument with all pages and full text.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the document exceeds max_pages.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pages: list[PageContent] = []
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > self.max_pages:
                raise ValueError(
                    f"Document has {len(pdf.pages)} pages, "
                    f"exceeds limit of {self.max_pages}"
                )

            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []
                pages.append(PageContent(page_number=i + 1, text=text, tables=tables))

        full_text = "\n\n".join(p.text for p in pages)
        logger.info("Extracted %d pages from %s", len(pages), pdf_path.name)

        return ExtractedDocument(
            filename=pdf_path.name,
            total_pages=len(pages),
            pages=pages,
            full_text=full_text,
        )

    def extract_streaming(self, pdf_path: str | Path) -> Iterator[PageContent]:
        """Memory-efficient page-by-page extraction.

        Args:
            pdf_path: Path to the PDF file.

        Yields:
            PageContent for each page up to max_pages.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[: self.max_pages]):
                yield PageContent(
                    page_number=i + 1,
                    text=page.extract_text() or "",
                    tables=page.extract_tables() or [],
                )
