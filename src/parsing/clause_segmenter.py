"""Clause segmentation for contract documents.

Splits contract text into individual clauses based on numbering
patterns and bullet points.
"""

import re
from dataclasses import dataclass


@dataclass
class Clause:
    """A single clause extracted from a contract."""

    id: str
    text: str
    section_type: str
    position: int


class ClauseSegmenter:
    """Segments contract text into individual clauses.

    Identifies clause boundaries using numbered patterns (1.1, 2.3),
    lettered sub-clauses (a), b)), and bullet points.
    """

    CLAUSE_PATTERN: re.Pattern[str] = re.compile(
        r"(?:^|\n)\s*(?:(\d+(?:\.\d+)*)\s*\.?\s*|([a-z])\)\s*|\u2022\s*)"
    )

    def segment(self, text: str, section_type: str = "unknown") -> list[Clause]:
        """Segment text into individual clauses.

        Args:
            text: Contract text to segment.
            section_type: Section type label for the clauses.

        Returns:
            List of Clause objects extracted from the text.
        """
        clauses: list[Clause] = []
        matches = list(self.CLAUSE_PATTERN.finditer(text))

        if not matches:
            stripped = text.strip()
            if stripped:
                return [
                    Clause(
                        id="1",
                        text=stripped,
                        section_type=section_type,
                        position=0,
                    )
                ]
            return []

        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            clause_id = match.group(1) or match.group(2) or str(i + 1)
            clause_text = text[start:end].strip()
            if clause_text:
                clauses.append(
                    Clause(
                        id=clause_id,
                        text=clause_text,
                        section_type=section_type,
                        position=i,
                    )
                )

        return clauses
