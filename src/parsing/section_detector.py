"""Section detection for contract documents.

Identifies and classifies sections within contract text based on
heading patterns and keyword matching.
"""

import re
from dataclasses import dataclass
from enum import Enum


class SectionType(Enum):
    """Contract section type classification."""

    PREAMBLE = "preamble"
    DEFINITIONS = "definitions"
    OBLIGATIONS = "obligations"
    PAYMENT = "payment"
    TERMINATION = "termination"
    CONFIDENTIALITY = "confidentiality"
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    DISPUTE_RESOLUTION = "dispute_resolution"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """A detected section within a contract document."""

    section_type: SectionType
    title: str
    content: str
    start_line: int
    end_line: int


SECTION_PATTERNS: dict[SectionType, str] = {
    SectionType.DEFINITIONS: (r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*definitions?"),
    SectionType.OBLIGATIONS: (
        r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*"
        r"(?:obligations?|duties|responsibilities)"
    ),
    SectionType.PAYMENT: (
        r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*(?:payment|compensation|fees)"
    ),
    SectionType.TERMINATION: (r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*termination"),
    SectionType.CONFIDENTIALITY: (
        r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*confidential"
    ),
    SectionType.LIABILITY: (
        r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*(?:limitation of )?liability"
    ),
    SectionType.INDEMNIFICATION: (r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*indemnif"),
    SectionType.DISPUTE_RESOLUTION: (
        r"(?i)^\s*(?:article|section)?\s*\d*\.?\s*"
        r"(?:dispute|arbitration|governing law)"
    ),
}


class SectionDetector:
    """Detects and classifies sections in contract text."""

    def detect_sections(self, text: str) -> list[Section]:
        """Detect all sections in the given contract text.

        Args:
            text: Full text of the contract document.

        Returns:
            List of detected Section objects. Falls back to a single
            UNKNOWN section if no sections are detected.
        """
        lines = text.split("\n")
        sections: list[Section] = []
        current_section: SectionType | None = None
        current_start = 0
        current_content: list[str] = []

        for i, line in enumerate(lines):
            section_type = self._classify_line(line)
            if section_type and section_type != SectionType.UNKNOWN:
                if current_section:
                    sections.append(
                        Section(
                            section_type=current_section,
                            title=lines[current_start].strip(),
                            content="\n".join(current_content),
                            start_line=current_start,
                            end_line=i - 1,
                        )
                    )
                current_section = section_type
                current_start = i
                current_content = [line]
            else:
                current_content.append(line)

        if current_section:
            sections.append(
                Section(
                    section_type=current_section,
                    title=lines[current_start].strip(),
                    content="\n".join(current_content),
                    start_line=current_start,
                    end_line=len(lines) - 1,
                )
            )

        if not sections:
            return [Section(SectionType.UNKNOWN, "", text, 0, len(lines) - 1)]
        return sections

    def _classify_line(self, line: str) -> SectionType | None:
        """Classify a line as a section heading or None.

        Args:
            line: A single line of text.

        Returns:
            The SectionType if the line matches a section pattern, else None.
        """
        for section_type, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line):
                return section_type
        return None
