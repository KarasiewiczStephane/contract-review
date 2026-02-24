"""Tests for compliance checker module."""

from pathlib import Path

import pytest
import yaml

from src.analysis.compliance_checker import (
    ComplianceChecker,
    ComplianceResult,
    ComplianceRule,
)


@pytest.fixture()
def checker() -> ComplianceChecker:
    """Create a ComplianceChecker with default rules."""
    return ComplianceChecker(rules_path="nonexistent_for_defaults.yaml")


@pytest.fixture()
def rules_file(tmp_path: Path) -> Path:
    """Create a temporary compliance rules file."""
    rules = {
        "rules": [
            {
                "id": "test_1",
                "name": "Test Rule",
                "description": "A test rule",
                "required_keywords": ["test keyword"],
                "category": "Test",
            }
        ]
    }
    path = tmp_path / "rules.yaml"
    path.write_text(yaml.dump(rules))
    return path


def test_default_rules_loaded(checker: ComplianceChecker) -> None:
    """Test that default rules are loaded when file doesn't exist."""
    assert len(checker.rules) == 3
    assert checker.rules[0].id == "gdpr_1"


def test_load_custom_rules(rules_file: Path) -> None:
    """Test loading custom rules from YAML file."""
    checker = ComplianceChecker(rules_path=str(rules_file))
    assert len(checker.rules) == 1
    assert checker.rules[0].id == "test_1"


def test_check_compliant(checker: ComplianceChecker) -> None:
    """Test checking text that satisfies a rule."""
    text = "This contract covers personal data processing under GDPR."
    results = checker.check(text)
    gdpr_result = next(r for r in results if r.rule.id == "gdpr_1")
    assert gdpr_result.compliant is True
    assert gdpr_result.evidence is not None


def test_check_non_compliant(checker: ComplianceChecker) -> None:
    """Test checking text that doesn't satisfy a rule."""
    text = "This is a basic contract about widgets."
    results = checker.check(text)
    assert all(r.compliant is False for r in results)


def test_check_with_category_filter(checker: ComplianceChecker) -> None:
    """Test filtering rules by category."""
    text = "This includes limitation of liability terms."
    results = checker.check(text, categories=["Standard"])
    assert len(results) == 1
    assert results[0].rule.category == "Standard"


def test_check_evidence_extraction(checker: ComplianceChecker) -> None:
    """Test that evidence is extracted around the matching keyword."""
    text = "Prefix text. This agreement involves personal data processing. Suffix text."
    results = checker.check(text)
    gdpr_result = next(r for r in results if r.rule.id == "gdpr_1")
    assert gdpr_result.evidence is not None
    assert "personal data" in gdpr_result.evidence


def test_check_no_evidence_when_non_compliant(checker: ComplianceChecker) -> None:
    """Test that evidence is None for non-compliant rules."""
    text = "Generic text with no relevant terms."
    results = checker.check(text)
    for r in results:
        if not r.compliant:
            assert r.evidence is None


def test_compliance_rule_dataclass() -> None:
    """Test ComplianceRule dataclass."""
    rule = ComplianceRule(
        id="r1",
        name="Rule 1",
        description="Desc",
        required_keywords=["kw1"],
        category="Cat1",
    )
    assert rule.id == "r1"
    assert rule.name == "Rule 1"


def test_compliance_result_dataclass() -> None:
    """Test ComplianceResult dataclass."""
    rule = ComplianceRule("r1", "Rule", "Desc", ["kw"], "Cat")
    result = ComplianceResult(rule=rule, compliant=True, evidence="found kw here")
    assert result.compliant is True
    assert "kw" in result.evidence


def test_check_empty_text(checker: ComplianceChecker) -> None:
    """Test checking empty text returns non-compliant results."""
    results = checker.check("")
    assert all(r.compliant is False for r in results)


def test_check_case_insensitive(checker: ComplianceChecker) -> None:
    """Test that keyword matching is case-insensitive."""
    text = "This contract references PERSONAL DATA requirements."
    results = checker.check(text)
    gdpr_result = next(r for r in results if r.rule.id == "gdpr_1")
    assert gdpr_result.compliant is True
