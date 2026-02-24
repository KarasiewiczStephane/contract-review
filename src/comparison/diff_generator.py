"""Diff generation and comparison report creation.

Generates structured comparison reports from clause alignments,
including summary statistics, risk comparisons, and markdown output.
"""

import logging
from dataclasses import dataclass

from src.analysis.clause_analyzer import ClauseAnalysis
from src.comparison.aligner import ClauseAlignment
from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class ComparisonReport:
    """Complete comparison report between two contracts."""

    summary: dict[str, int]
    alignments: list[ClauseAlignment]
    risk_comparison: dict[str, dict[str, int]]
    markdown: str


class DiffGenerator:
    """Generates comparison reports from clause alignments."""

    def generate(
        self,
        alignments: list[ClauseAlignment],
        analyses_a: list[ClauseAnalysis] | None = None,
        analyses_b: list[ClauseAnalysis] | None = None,
    ) -> ComparisonReport:
        """Generate a comparison report from alignments.

        Args:
            alignments: List of clause alignments.
            analyses_a: Optional clause analyses for contract A.
            analyses_b: Optional clause analyses for contract B.

        Returns:
            ComparisonReport with summary, alignments, and markdown.
        """
        summary: dict[str, int] = {
            "matched": sum(1 for a in alignments if a.match_type == "matched"),
            "modified": sum(1 for a in alignments if a.match_type == "modified"),
            "added": sum(1 for a in alignments if a.match_type == "added"),
            "removed": sum(1 for a in alignments if a.match_type == "removed"),
        }

        risk_comparison: dict[str, dict[str, int]] = {}
        if analyses_a and analyses_b:
            risk_comparison = {
                "contract_a": self._risk_summary(analyses_a),
                "contract_b": self._risk_summary(analyses_b),
            }

        markdown = self._generate_markdown(alignments, summary, risk_comparison)

        logger.info("Generated comparison report: %s", summary)

        return ComparisonReport(
            summary=summary,
            alignments=alignments,
            risk_comparison=risk_comparison,
            markdown=markdown,
        )

    def _risk_summary(self, analyses: list[ClauseAnalysis]) -> dict[str, int]:
        """Summarize risk levels from clause analyses.

        Args:
            analyses: List of clause analyses.

        Returns:
            Dictionary with counts per risk level.
        """
        return {
            "high": sum(1 for a in analyses if a.risk_level == "high"),
            "medium": sum(1 for a in analyses if a.risk_level == "medium"),
            "low": sum(1 for a in analyses if a.risk_level == "low"),
        }

    def _generate_markdown(
        self,
        alignments: list[ClauseAlignment],
        summary: dict[str, int],
        risk: dict[str, dict[str, int]],
    ) -> str:
        """Generate markdown report from comparison data.

        Args:
            alignments: Clause alignments.
            summary: Summary statistics.
            risk: Risk comparison data.

        Returns:
            Markdown-formatted report string.
        """
        md: list[str] = ["# Contract Comparison Report\n"]
        md.append("## Summary\n")
        md.append(f"- Matched clauses: {summary['matched']}")
        md.append(f"- Modified clauses: {summary['modified']}")
        md.append(f"- Added clauses: {summary['added']}")
        md.append(f"- Removed clauses: {summary['removed']}\n")

        if risk:
            md.append("## Risk Comparison\n")
            md.append("| Risk Level | Contract A | Contract B |")
            md.append("|------------|------------|------------|")
            for level in ["high", "medium", "low"]:
                md.append(
                    f"| {level.title()} "
                    f"| {risk['contract_a'][level]} "
                    f"| {risk['contract_b'][level]} |"
                )
            md.append("")

        md.append("## Clause Details\n")
        for a in alignments:
            if a.match_type == "modified" and a.clause_a and a.clause_b:
                md.append(f"### Modified: Clause {a.clause_a.id}")
                md.append(f"**Contract A:** {a.clause_a.text[:200]}...")
                md.append(f"**Contract B:** {a.clause_b.text[:200]}...")
                md.append(f"*Similarity: {a.similarity:.0%}*\n")

        return "\n".join(md)
