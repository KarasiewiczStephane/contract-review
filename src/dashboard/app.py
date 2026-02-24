"""Streamlit dashboard for contract review.

Provides a web interface for uploading, analyzing, and reviewing
contract documents with risk assessment and clause analysis.
"""

import json
import tempfile

import streamlit as st

from src.analysis.clause_analyzer import ClauseAnalyzer
from src.analysis.compliance_checker import ComplianceChecker
from src.analysis.llm_client import AnthropicClient, OpenAIClient
from src.analysis.risk_scorer import RiskScorer
from src.parsing.clause_segmenter import ClauseSegmenter
from src.parsing.metadata_extractor import MetadataExtractor
from src.parsing.pdf_extractor import PDFExtractor
from src.parsing.section_detector import SectionDetector
from src.utils.config import load_config
from src.utils.cost_tracker import CostTracker

st.set_page_config(page_title="Contract Review", page_icon="\U0001f4c4", layout="wide")


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    if "cost_tracker" not in st.session_state:
        st.session_state.cost_tracker = CostTracker()


def get_llm_client(provider: str, model: str) -> OpenAIClient | AnthropicClient:
    """Create an LLM client based on provider selection.

    Args:
        provider: LLM provider name.
        model: Model identifier.

    Returns:
        Configured LLM client instance.
    """
    config = load_config()
    if provider == "OpenAI":
        return OpenAIClient(config.openai_api_key, model=model)
    return AnthropicClient(config.anthropic_api_key, model=model)


def main() -> None:
    """Main dashboard entry point."""
    init_session_state()
    st.title("\U0001f4c4 Contract Review")

    with st.sidebar:
        st.header("Settings")
        provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic"])
        models = (
            ["gpt-4", "gpt-3.5-turbo"]
            if provider == "OpenAI"
            else ["claude-3-opus", "claude-3-sonnet"]
        )
        model = st.selectbox("Model", models)

        if st.session_state.analyzed:
            st.divider()
            st.subheader("Cost Tracking")
            summary = st.session_state.cost_tracker.summary()
            st.metric("Total Cost", summary["total_cost"])
            st.metric("API Calls", summary["num_requests"])

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "\U0001f4e4 Upload",
            "\U0001f4ca Overview",
            "\U0001f4cb Clauses",
            "\u26a0\ufe0f Risk Report",
        ]
    )

    with tab1:
        render_upload_tab(provider, model)
    with tab2:
        render_overview_tab()
    with tab3:
        render_clauses_tab()
    with tab4:
        render_risk_tab()


def render_upload_tab(provider: str, model: str) -> None:
    """Render the file upload and analysis tab.

    Args:
        provider: Selected LLM provider.
        model: Selected model.
    """
    st.header("Upload Contract")
    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded and st.button("Analyze Contract"):
        with st.spinner("Extracting text..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            extractor = PDFExtractor()
            doc = extractor.extract(tmp_path)
            st.session_state.document = doc

        with st.spinner("Detecting sections..."):
            detector = SectionDetector()
            sections = detector.detect_sections(doc.full_text)
            st.session_state.sections = sections

        with st.spinner("Extracting metadata..."):
            meta_extractor = MetadataExtractor()
            metadata = meta_extractor.extract(doc.full_text)
            st.session_state.metadata = metadata

        with st.spinner("Analyzing clauses..."):
            segmenter = ClauseSegmenter()
            clauses = []
            for section in sections:
                clauses.extend(
                    segmenter.segment(section.content, section.section_type.value)
                )

            llm = get_llm_client(provider, model)
            analyzer = ClauseAnalyzer(llm)
            analyses = analyzer.analyze_batch(clauses[:20])
            st.session_state.analyses = analyses

            scorer = RiskScorer()
            risk_report = scorer.score(analyses)
            st.session_state.risk_report = risk_report

            checker = ComplianceChecker()
            compliance = checker.check(doc.full_text)
            st.session_state.compliance = compliance

        st.session_state.analyzed = True
        st.success("Contract analyzed successfully!")
        st.rerun()


def render_overview_tab() -> None:
    """Render the contract overview tab."""
    if not st.session_state.get("analyzed"):
        st.info("Upload and analyze a contract to see the overview.")
        return

    st.header("Contract Overview")
    metadata = st.session_state.metadata
    risk_report = st.session_state.risk_report

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Score", f"{risk_report.overall_score:.0f}/100")
    with col2:
        st.metric("Risk Level", risk_report.risk_level.upper())
    with col3:
        st.metric("Pages", st.session_state.document.total_pages)

    st.subheader("Parties")
    for party in metadata.parties:
        st.write(f"\u2022 {party}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Effective Date")
        st.write(
            str(metadata.effective_date) if metadata.effective_date else "Not detected"
        )
    with col2:
        st.subheader("Governing Law")
        st.write(metadata.governing_law or "Not detected")


def render_clauses_tab() -> None:
    """Render the clause explorer tab."""
    if not st.session_state.get("analyzed"):
        st.info("Upload and analyze a contract to see clauses.")
        return

    st.header("Clause Explorer")
    for analysis in st.session_state.analyses:
        color = {"low": "green", "medium": "orange", "high": "red"}.get(
            analysis.risk_level, "gray"
        )
        with st.expander(
            f":{color}[{analysis.risk_level.upper()}] "
            f"{analysis.clause_type} - Clause {analysis.clause_id}"
        ):
            st.write(f"**Summary:** {analysis.summary}")
            st.write(f"**Risk Reasoning:** {analysis.risk_reasoning}")
            if analysis.key_terms:
                st.write(f"**Key Terms:** {', '.join(analysis.key_terms)}")
            st.text(analysis.clause_text[:500])


def render_risk_tab() -> None:
    """Render the risk report tab."""
    if not st.session_state.get("analyzed"):
        st.info("Upload and analyze a contract to see the risk report.")
        return

    st.header("Risk Report")
    risk_report = st.session_state.risk_report

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Score", f"{risk_report.overall_score:.0f}/100")
        st.metric("Risk Level", risk_report.risk_level.upper())
    with col2:
        st.metric("High Risk Clauses", len(risk_report.high_risk_clauses))
        st.metric("Missing Clauses", len(risk_report.missing_clauses))

    if risk_report.missing_clauses:
        st.subheader("Missing Standard Clauses")
        for clause in risk_report.missing_clauses:
            st.warning(f"Missing: {clause}")

    if risk_report.recommendations:
        st.subheader("Recommendations")
        for rec in risk_report.recommendations:
            st.write(f"\u2022 {rec}")

    if st.session_state.get("compliance"):
        st.subheader("Compliance Check")
        for result in st.session_state.compliance:
            status = "\u2705" if result.compliant else "\u274c"
            st.write(f"{status} **{result.rule.name}** ({result.rule.category})")
            if result.evidence:
                st.caption(f"Evidence: ...{result.evidence}...")

    if st.button("Export Report as JSON"):
        report_data = {
            "overall_score": risk_report.overall_score,
            "risk_level": risk_report.risk_level,
            "missing_clauses": risk_report.missing_clauses,
            "recommendations": risk_report.recommendations,
            "clause_count": len(st.session_state.analyses),
        }
        st.download_button(
            "Download JSON",
            data=json.dumps(report_data, indent=2),
            file_name="risk_report.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
