"""Metadata extraction from contract documents.

Extracts parties, dates, governing law, and contract type from
contract text using NLP and regex patterns.
"""

import logging
import re
from dataclasses import dataclass
from datetime import date

from dateutil import parser as date_parser

from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class ContractMetadata:
    """Extracted metadata from a contract document."""

    parties: list[str]
    effective_date: date | None
    governing_law: str | None
    contract_type: str | None
    expiration_date: date | None


class MetadataExtractor:
    """Extracts structured metadata from contract text.

    Uses spaCy NER for party detection and regex for dates,
    governing law, and contract type classification.
    """

    DATE_PATTERNS: list[str] = [
        r"(?:effective|dated?)\s+(?:as of\s+)?([A-Z][a-z]+ \d{1,2},? \d{4})",
        r"(?:effective|dated?)\s+(?:as of\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(?:this|the)\s+\d{1,2}(?:st|nd|rd|th)?\s+day of\s+([A-Z][a-z]+),?\s+(\d{4})",
    ]

    GOVERNING_LAW_PATTERN: re.Pattern[str] = re.compile(
        r"(?:governed by|construed (?:in accordance with|under))\s+"
        r"(?:the )?laws? of\s+(?:the )?([A-Z][\w\s,]+?)(?:\.|,|\n)",
        re.IGNORECASE,
    )

    TYPE_KEYWORDS: dict[str, list[str]] = {
        "nda": ["non-disclosure", "confidentiality agreement", "nda"],
        "employment": ["employment agreement", "employment contract"],
        "service": ["service agreement", "master service"],
        "license": ["license agreement", "software license"],
        "lease": ["lease agreement", "rental agreement"],
    }

    def __init__(self, nlp: object | None = None) -> None:
        """Initialize the metadata extractor.

        Args:
            nlp: A spaCy language model. If None, attempts to load en_core_web_sm.
        """
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                import spacy

                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning(
                    "spaCy model 'en_core_web_sm' not found. "
                    "Party extraction via NER will be unavailable."
                )
                self.nlp = None

    def extract(self, text: str) -> ContractMetadata:
        """Extract metadata from contract text.

        Args:
            text: Full text of the contract document.

        Returns:
            ContractMetadata with extracted fields.
        """
        preamble = text[:3000]

        return ContractMetadata(
            parties=self._extract_parties(preamble),
            effective_date=self._extract_date(preamble),
            governing_law=self._extract_governing_law(text),
            contract_type=self._detect_contract_type(text),
            expiration_date=None,
        )

    def _extract_parties(self, text: str) -> list[str]:
        """Extract party names from contract preamble.

        Args:
            text: Preamble text of the contract.

        Returns:
            List of unique party names (up to 5).
        """
        parties: list[str] = []

        if self.nlp is not None:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    parties.append(ent.text)

        between_match = re.search(
            r"between\s+([^,]+?)\s+(?:,\s*)?(?:and|&)\s+([^,]+?)(?:,|\.|\()",
            text,
            re.IGNORECASE,
        )
        if between_match:
            parties.extend(
                [between_match.group(1).strip(), between_match.group(2).strip()]
            )

        return list(dict.fromkeys(parties))[:5]

    def _extract_date(self, text: str) -> date | None:
        """Extract the effective date from contract text.

        Args:
            text: Contract preamble text.

        Returns:
            Parsed date or None if not found.
        """
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return date_parser.parse(match.group(1)).date()
                except (ValueError, TypeError):
                    continue
        return None

    def _extract_governing_law(self, text: str) -> str | None:
        """Extract governing law jurisdiction from contract text.

        Args:
            text: Full contract text.

        Returns:
            Jurisdiction name or None.
        """
        match = self.GOVERNING_LAW_PATTERN.search(text)
        return match.group(1).strip() if match else None

    def _detect_contract_type(self, text: str) -> str | None:
        """Detect the type of contract based on keyword matching.

        Args:
            text: Full contract text.

        Returns:
            Contract type string or None.
        """
        text_lower = text[:2000].lower()
        for contract_type, keywords in self.TYPE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return contract_type
        return None
