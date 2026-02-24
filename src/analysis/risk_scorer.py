"""Risk scoring for analyzed contract clauses.

Computes an overall risk score, identifies high-risk clauses,
and checks for missing standard contract sections.
"""

import logging
from dataclasses import dataclass

from src.analysis.clause_analyzer import ClauseAnalysis
from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class RiskReport:
    """Aggregated risk assessment for a contract."""

    overall_score: float
    risk_level: str
    high_risk_clauses: list[ClauseAnalysis]
    missing_clauses: list[str]
    unusual_terms: list[str]
    recommendations: list[str]


class RiskScorer:
    """Scores contract risk based on clause analyses.

    Uses weighted scoring of individual clause risk levels
    and checks for expected standard clauses.
    """

    RISK_WEIGHTS: dict[str, int] = {"low": 1, "medium": 2, "high": 3}
    EXPECTED_CLAUSES: list[str] = [
        "liability",
        "termination",
        "confidentiality",
        "dispute_resolution",
    ]

    def score(self, analyses: list[ClauseAnalysis]) -> RiskReport:
        """Compute a risk report from clause analyses.

        Args:
            analyses: List of analyzed clauses.

        Returns:
            RiskReport with overall score and recommendations.
        """
        if not analyses:
            return RiskReport(50.0, "medium", [], [], [], [])

        total_weight = sum(self.RISK_WEIGHTS.get(a.risk_level, 2) for a in analyses)
        max_weight = len(analyses) * 3
        score = (total_weight / max_weight) * 100

        high_risk = [a for a in analyses if a.risk_level == "high"]

        present_types = {a.clause_type for a in analyses}
        missing = [c for c in self.EXPECTED_CLAUSES if c not in present_types]

        recommendations = self._generate_recommendations(high_risk, missing)

        logger.info(
            "Risk score: %.1f (%s), %d high-risk clauses, %d missing",
            score,
            self._score_to_level(score),
            len(high_risk),
            len(missing),
        )

        return RiskReport(
            overall_score=round(score, 1),
            risk_level=self._score_to_level(score),
            high_risk_clauses=high_risk,
            missing_clauses=missing,
            unusual_terms=[],
            recommendations=recommendations,
        )

    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level label.

        Args:
            score: Numeric risk score (0-100).

        Returns:
            Risk level string: low, medium, or high.
        """
        if score < 40:
            return "low"
        elif score < 70:
            return "medium"
        return "high"

    def _generate_recommendations(
        self,
        high_risk: list[ClauseAnalysis],
        missing: list[str],
    ) -> list[str]:
        """Generate actionable recommendations.

        Args:
            high_risk: High-risk clause analyses.
            missing: Names of missing expected clauses.

        Returns:
            List of recommendation strings.
        """
        recs: list[str] = []
        for clause in high_risk:
            recs.append(f"Review {clause.clause_type} clause: {clause.risk_reasoning}")
        for m in missing:
            recs.append(f"Consider adding {m} clause")
        return recs
