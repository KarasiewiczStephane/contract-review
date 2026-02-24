"""Compliance checking against configurable rule sets.

Checks contract text against a set of compliance rules loaded
from YAML configuration or built-in defaults.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.utils.logger import setup_logger

logger: logging.Logger = setup_logger(__name__)


@dataclass
class ComplianceRule:
    """A single compliance rule definition."""

    id: str
    name: str
    description: str
    required_keywords: list[str]
    category: str


@dataclass
class ComplianceResult:
    """Result of checking a single compliance rule."""

    rule: ComplianceRule
    compliant: bool
    evidence: str | None


class ComplianceChecker:
    """Checks contract text against compliance rules.

    Args:
        rules_path: Path to YAML file containing compliance rules.
    """

    def __init__(self, rules_path: str = "configs/compliance_rules.yaml") -> None:
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: str) -> list[ComplianceRule]:
        """Load rules from YAML file or use defaults.

        Args:
            path: Path to the compliance rules YAML file.

        Returns:
            List of ComplianceRule instances.
        """
        if not Path(path).exists():
            logger.info("No rules file at %s, using defaults", path)
            return self._default_rules()
        with open(path) as f:
            data = yaml.safe_load(f)
        return [ComplianceRule(**r) for r in data.get("rules", [])]

    def _default_rules(self) -> list[ComplianceRule]:
        """Provide built-in default compliance rules.

        Returns:
            List of default ComplianceRule instances.
        """
        return [
            ComplianceRule(
                "gdpr_1",
                "Data Processing Terms",
                "Contract should specify data processing purposes",
                ["data process", "personal data", "gdpr"],
                "GDPR",
            ),
            ComplianceRule(
                "gdpr_2",
                "Data Subject Rights",
                "Must reference data subject rights",
                ["data subject", "right to access", "erasure"],
                "GDPR",
            ),
            ComplianceRule(
                "std_1",
                "Limitation of Liability",
                "Should include liability cap",
                ["limitation of liability", "liability cap", "maximum liability"],
                "Standard",
            ),
        ]

    def check(
        self,
        text: str,
        categories: list[str] | None = None,
    ) -> list[ComplianceResult]:
        """Check contract text against compliance rules.

        Args:
            text: Full contract text.
            categories: Optional list of categories to filter rules by.

        Returns:
            List of ComplianceResult for each applicable rule.
        """
        text_lower = text.lower()
        results: list[ComplianceResult] = []

        for rule in self.rules:
            if categories and rule.category not in categories:
                continue
            found = any(kw in text_lower for kw in rule.required_keywords)
            evidence = None
            if found:
                for kw in rule.required_keywords:
                    if kw in text_lower:
                        idx = text_lower.find(kw)
                        evidence = text[max(0, idx - 50) : idx + len(kw) + 50]
                        break
            results.append(
                ComplianceResult(rule=rule, compliant=found, evidence=evidence)
            )

        logger.info(
            "Checked %d rules, %d compliant",
            len(results),
            sum(1 for r in results if r.compliant),
        )
        return results
