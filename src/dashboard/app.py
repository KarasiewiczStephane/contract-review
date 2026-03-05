"""Streamlit dashboard for contract review.

Provides a web interface for uploading, analyzing, and reviewing
contract documents with risk assessment and clause analysis.
"""

import json
import tempfile
from pathlib import Path

import streamlit as st

from src.analysis.clause_analyzer import ClauseAnalyzer
from src.analysis.compliance_checker import ComplianceChecker
from src.analysis.llm_client import AnthropicClient, DemoClient, OpenAIClient
from src.analysis.risk_scorer import RiskScorer
from src.comparison.aligner import ClauseAligner
from src.comparison.diff_generator import DiffGenerator
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


def get_llm_client(provider: str, model: str) -> DemoClient | OpenAIClient | AnthropicClient:
    """Create an LLM client based on provider selection.

    Args:
        provider: LLM provider name.
        model: Model identifier.

    Returns:
        Configured LLM client instance.
    """
    if provider.startswith("Demo"):
        return DemoClient()
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
        provider = st.selectbox("LLM Provider", ["Demo (No API needed)", "Anthropic", "OpenAI"])
        if provider == "Anthropic":
            models = ["claude-sonnet-4-20250514", "claude-haiku-4-20250414"]
        elif provider == "OpenAI":
            models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        else:
            models = ["demo"]
        model = st.selectbox("Model", models)

        if st.session_state.analyzed:
            st.divider()
            st.subheader("Cost Tracking")
            summary = st.session_state.cost_tracker.summary()
            st.metric("Total Cost", summary["total_cost"])
            st.metric("API Calls", summary["num_requests"])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "\U0001f4e4 Upload",
            "\U0001f4ca Overview",
            "\U0001f4cb Clauses",
            "\u26a0\ufe0f Risk Report",
            "\U0001f504 Compare",
            "\U0001f4be Export",
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
    with tab5:
        render_comparison_tab()
    with tab6:
        render_export_tab()


def render_upload_tab(provider: str, model: str) -> None:
    """Render the file upload and analysis tab.

    Args:
        provider: Selected LLM provider.
        model: Selected model.
    """
    st.header("Upload Contract")

    sample_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sample"
    sample_files = sorted(sample_dir.glob("*.pdf")) if sample_dir.exists() else []

    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

    if sample_files:
        st.markdown("**Or try a sample contract:**")
        cols = st.columns(len(sample_files))
        for col, sample in zip(cols, sample_files):
            with col:
                if st.button(sample.stem.replace("sample_", "").replace("_", " ").title(), key=sample.name):
                    st.session_state.sample_path = str(sample)
                    st.rerun()

    sample_path = st.session_state.pop("sample_path", None)
    if sample_path:
        uploaded = None
        tmp_path = sample_path
        st.info(f"Using sample: {Path(sample_path).name}")
    elif uploaded:
        tmp_path = None
    else:
        tmp_path = None

    if (uploaded or sample_path) and (st.button("Analyze Contract") if not sample_path else True):
        with st.spinner("Extracting text..."):
            if uploaded and not tmp_path:
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


def render_comparison_tab() -> None:
    """Render the contract comparison tab."""
    st.header("Contract Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contract A")
        file_a = st.file_uploader(
            "Upload first contract", type=["pdf"], key="compare_a"
        )
    with col2:
        st.subheader("Contract B")
        file_b = st.file_uploader(
            "Upload second contract", type=["pdf"], key="compare_b"
        )

    if file_a and file_b and st.button("Compare Contracts"):
        with st.spinner("Analyzing contracts..."):
            extractor = PDFExtractor()
            segmenter = ClauseSegmenter()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_a.read())
                doc_a = extractor.extract(tmp.name)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_b.read())
                doc_b = extractor.extract(tmp.name)

            clauses_a = segmenter.segment(doc_a.full_text)
            clauses_b = segmenter.segment(doc_b.full_text)

            aligner = ClauseAligner()
            alignments = aligner.align(clauses_a, clauses_b)

            diff_gen = DiffGenerator()
            report = diff_gen.generate(alignments)
            st.session_state.comparison = report

        st.success("Comparison complete!")

    if st.session_state.get("comparison"):
        report = st.session_state.comparison

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Matched", report.summary["matched"])
        col2.metric("Modified", report.summary["modified"])
        col3.metric("Added", report.summary["added"])
        col4.metric("Removed", report.summary["removed"])

        st.divider()

        for align in report.alignments:
            if align.match_type == "matched":
                continue

            c1, c2 = st.columns(2)
            if align.match_type == "modified" and align.clause_a and align.clause_b:
                with c1:
                    st.markdown(f"**Contract A - Clause {align.clause_a.id}**")
                    st.text(align.clause_a.text[:300])
                with c2:
                    st.markdown(f"**Contract B - Clause {align.clause_b.id}**")
                    st.text(align.clause_b.text[:300])
                st.caption(f"Similarity: {align.similarity:.0%}")
                st.divider()
            elif align.match_type == "removed" and align.clause_a:
                with c1:
                    st.error(f"**Removed:** {align.clause_a.text[:200]}")
                with c2:
                    st.write("\u2014")
            elif align.match_type == "added" and align.clause_b:
                with c1:
                    st.write("\u2014")
                with c2:
                    st.success(f"**Added:** {align.clause_b.text[:200]}")

        st.download_button(
            "Download Comparison Report",
            data=report.markdown,
            file_name="comparison_report.md",
            mime="text/markdown",
        )


def render_export_tab() -> None:
    """Render the export tab."""
    if not st.session_state.get("analyzed"):
        st.info("Analyze a contract first to export results.")
        return

    st.header("Export Analysis")
    metadata = st.session_state.metadata
    risk_report = st.session_state.risk_report

    export_data = {
        "metadata": {
            "parties": metadata.parties,
            "effective_date": str(metadata.effective_date),
            "governing_law": metadata.governing_law,
            "contract_type": metadata.contract_type,
        },
        "risk_report": {
            "overall_score": risk_report.overall_score,
            "risk_level": risk_report.risk_level,
            "missing_clauses": risk_report.missing_clauses,
            "recommendations": risk_report.recommendations,
        },
        "clauses": [
            {
                "id": a.clause_id,
                "type": a.clause_type,
                "risk_level": a.risk_level,
                "summary": a.summary,
                "key_terms": a.key_terms,
            }
            for a in st.session_state.analyses
        ],
    }

    st.json(export_data)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download as JSON",
            data=json.dumps(export_data, indent=2, default=str),
            file_name="contract_analysis.json",
            mime="application/json",
        )
    with col2:
        markdown_report = _build_markdown_report(metadata, risk_report)
        st.download_button(
            "Download as Markdown",
            data=markdown_report,
            file_name="contract_analysis.md",
            mime="text/markdown",
        )


def _build_markdown_report(metadata: object, risk_report: object) -> str:
    """Build a markdown report from analysis results.

    Args:
        metadata: Contract metadata.
        risk_report: Risk assessment report.

    Returns:
        Markdown-formatted report string.
    """
    lines = [
        "# Contract Analysis Report\n",
        "## Metadata\n",
        f"- **Parties:** {', '.join(metadata.parties)}",
        f"- **Effective Date:** {metadata.effective_date}",
        f"- **Governing Law:** {metadata.governing_law}",
        f"- **Contract Type:** {metadata.contract_type}\n",
        "## Risk Assessment\n",
        f"- **Overall Score:** {risk_report.overall_score}/100",
        f"- **Risk Level:** {risk_report.risk_level}\n",
    ]
    if risk_report.missing_clauses:
        lines.append("## Missing Clauses\n")
        for clause in risk_report.missing_clauses:
            lines.append(f"- {clause}")
    if risk_report.recommendations:
        lines.append("\n## Recommendations\n")
        for rec in risk_report.recommendations:
            lines.append(f"- {rec}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
