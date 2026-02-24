"""Clause analysis using LLM for risk assessment and classification.

Sends individual clauses to an LLM for structured analysis including
risk level, clause type, and key terms extraction.
"""

import json
import logging
from dataclasses import dataclass

from src.analysis.llm_client import LLMClient
from src.analysis.prompts import CLAUSE_ANALYSIS_PROMPT, CLAUSE_ANALYSIS_SYSTEM
from src.parsing.clause_segmenter import Clause
from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class ClauseAnalysis:
    """Result of analyzing a single clause."""

    clause_id: str
    clause_text: str
    clause_type: str
    risk_level: str
    risk_reasoning: str
    key_terms: list[str]
    summary: str


class ClauseAnalyzer:
    """Analyzes contract clauses using an LLM backend.

    Args:
        llm_client: An LLMClient instance for sending prompts.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def analyze(self, clause: Clause) -> ClauseAnalysis:
        """Analyze a single clause using the LLM.

        Args:
            clause: The clause to analyze.

        Returns:
            ClauseAnalysis with classification and risk assessment.
        """
        prompt = CLAUSE_ANALYSIS_PROMPT.format(clause_text=clause.text)
        response = self.llm.complete(prompt, system=CLAUSE_ANALYSIS_SYSTEM)

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response, using fallback")
            data = self._parse_fallback(response)

        return ClauseAnalysis(
            clause_id=clause.id,
            clause_text=clause.text,
            clause_type=data.get("clause_type", "other"),
            risk_level=data.get("risk_level", "medium"),
            risk_reasoning=data.get("risk_reasoning", ""),
            key_terms=data.get("key_terms", []),
            summary=data.get("summary", ""),
        )

    def analyze_batch(self, clauses: list[Clause]) -> list[ClauseAnalysis]:
        """Analyze multiple clauses sequentially.

        Args:
            clauses: List of clauses to analyze.

        Returns:
            List of ClauseAnalysis results.
        """
        return [self.analyze(c) for c in clauses]

    def _parse_fallback(self, response: str) -> dict[str, object]:
        """Fallback parser for malformed LLM JSON responses.

        Args:
            response: The raw LLM response text.

        Returns:
            Dictionary with default values and truncated summary.
        """
        return {
            "clause_type": "other",
            "risk_level": "medium",
            "risk_reasoning": "",
            "key_terms": [],
            "summary": response[:200],
        }
