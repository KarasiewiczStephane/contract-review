"""Clause alignment for contract comparison.

Aligns clauses from two contracts based on text similarity
to identify matched, modified, added, and removed clauses.
"""

import logging
from dataclasses import dataclass
from difflib import SequenceMatcher

from src.parsing.clause_segmenter import Clause
from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class ClauseAlignment:
    """Alignment result between two clauses."""

    clause_a: Clause | None
    clause_b: Clause | None
    similarity: float
    match_type: str


class ClauseAligner:
    """Aligns clauses from two contracts by text similarity.

    Args:
        similarity_threshold: Minimum similarity ratio for a match.
    """

    def __init__(self, similarity_threshold: float = 0.6) -> None:
        self.threshold = similarity_threshold

    def align(
        self,
        clauses_a: list[Clause],
        clauses_b: list[Clause],
    ) -> list[ClauseAlignment]:
        """Align clauses from two contracts.

        Args:
            clauses_a: Clauses from the first contract.
            clauses_b: Clauses from the second contract.

        Returns:
            List of ClauseAlignment results.
        """
        alignments: list[ClauseAlignment] = []
        used_b: set[int] = set()

        for ca in clauses_a:
            best_match: Clause | None = None
            best_sim = 0.0
            best_idx = -1

            for i, cb in enumerate(clauses_b):
                if i in used_b:
                    continue
                sim = self._similarity(ca.text, cb.text)
                if sim > best_sim:
                    best_sim = sim
                    best_match = cb
                    best_idx = i

            if best_sim >= self.threshold:
                used_b.add(best_idx)
                match_type = "matched" if best_sim > 0.95 else "modified"
                alignments.append(ClauseAlignment(ca, best_match, best_sim, match_type))
            else:
                alignments.append(ClauseAlignment(ca, None, 0, "removed"))

        for i, cb in enumerate(clauses_b):
            if i not in used_b:
                alignments.append(ClauseAlignment(None, cb, 0, "added"))

        logger.info(
            "Aligned %d clauses: %d matched, %d modified, %d added, %d removed",
            len(alignments),
            sum(1 for a in alignments if a.match_type == "matched"),
            sum(1 for a in alignments if a.match_type == "modified"),
            sum(1 for a in alignments if a.match_type == "added"),
            sum(1 for a in alignments if a.match_type == "removed"),
        )

        return alignments

    def _similarity(self, text_a: str, text_b: str) -> float:
        """Compute similarity ratio between two texts.

        Args:
            text_a: First text.
            text_b: Second text.

        Returns:
            Similarity ratio between 0 and 1.
        """
        return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()
