"""Prompt templates for LLM-based clause analysis."""

CLAUSE_ANALYSIS_SYSTEM: str = (
    "You are a legal document analyst. "
    "Analyze contract clauses and provide structured JSON output."
)

CLAUSE_ANALYSIS_PROMPT: str = """Analyze the following contract clause and return a JSON object with these fields:
- clause_type: one of [payment, liability, indemnification, termination, renewal, ip_ownership, confidentiality, non_compete, force_majeure, dispute_resolution, other]
- risk_level: one of [low, medium, high]
- risk_reasoning: brief explanation of risk assessment
- key_terms: list of important terms (dates, amounts, percentages)
- summary: plain language summary (1-2 sentences)

Clause:
\"\"\"
{clause_text}
\"\"\"

Return only valid JSON, no markdown formatting."""
