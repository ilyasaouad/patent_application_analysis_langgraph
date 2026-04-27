"""
streamlit_app_agent4_only.py
============================
Simplified app that runs ONLY Agent 4 (Claims Clarity Analysis).

Prerequisites:
    - output_text_documents/description.md
    - output_text_documents/claims.md
    - output_text_documents/drawings.md (optional)

This skips all extraction and previous agents.
"""

import os
import streamlit as st
from pathlib import Path

from agents.agent4_claims_clarity.claims_clarity_agent import (
    claims_clarity_agent,
)

st.set_page_config(page_title="Agent 4: Claims Clarity", page_icon="⚖️", layout="wide")

st.title("⚖️ Agent 4: Claims Clarity Analysis")
st.markdown("**NIPO § 8 Legal Analysis — Enablement | Clarity | Support**")
st.markdown("---")

# Directories
INPUT_DIR = Path("output_text_documents")
OUTPUT_DIR = Path("output_analysis_reports")
OUTPUT_DIR.mkdir(exist_ok=True)

# Check prerequisites
st.subheader("📋 Prerequisites Check")

desc_file = INPUT_DIR / "description.md"
claims_file = INPUT_DIR / "claims.md"
drawings_file = INPUT_DIR / "drawings.md"

has_desc = desc_file.exists() and desc_file.stat().st_size > 0
has_claims = claims_file.exists() and claims_file.stat().st_size > 0
has_drawings = drawings_file.exists() and drawings_file.stat().st_size > 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Description", "✅ Found" if has_desc else "❌ Missing")
with col2:
    st.metric("Claims", "✅ Found" if has_claims else "❌ Missing")
with col3:
    st.metric("Drawings", "✅ Found" if has_drawings else "⚪ Optional")

if not has_desc or not has_claims:
    st.error("""
    ❌ **Missing required files!**
    
    Please ensure these files exist in `output_text_documents/`:
    - `description.md`
    - `claims.md`
    
    Run the full extraction pipeline first (streamlit_app.py) to generate these files.
    """)
    st.stop()

# Load and show file info
st.markdown("---")
st.subheader("📄 Loaded Documents")

with open(desc_file, "r", encoding="utf-8") as f:
    description_text = f.read()
with open(claims_file, "r", encoding="utf-8") as f:
    claims_text = f.read()
drawings_text = ""
if has_drawings:
    with open(drawings_file, "r", encoding="utf-8") as f:
        drawings_text = f.read()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Description", f"{len(description_text):,} chars")
with col2:
    st.metric("Claims", f"{len(claims_text):,} chars")
with col3:
    st.metric("Drawings", f"{len(drawings_text):,} chars" if has_drawings else "N/A")

# Quick preview
with st.expander("🔍 Preview Documents"):
    tab1, tab2, tab3 = st.tabs(["Description", "Claims", "Drawings"])
    with tab1:
        st.text_area(
            "Description (first 1000 chars)", value=description_text[:1000], height=300
        )
    with tab2:
        st.text_area("Claims (first 1000 chars)", value=claims_text[:1000], height=300)
    with tab3:
        if has_drawings:
            st.text_area("Drawings", value=drawings_text[:1000], height=300)
        else:
            st.info("No drawings file")

# Run Agent 4
st.markdown("---")
st.subheader("⚖️ Run Claims Clarity Analysis")

if st.button("🔍 Analyze Patent (NIPO § 8)", type="primary", use_container_width=True):
    # Prepare state
    state = {
        "description_text": description_text,
        "claims_text": claims_text,
        "drawings_text": drawings_text,
        "claims_extracted_from_description": False,
        "ai_detection_results": None,
        "claims_clarity_results": None,
        "status": "READY",
        "error_message": None,
        "final_report": None,
        "proposal_letter": None,
    }

    with st.spinner(
        "Running NIPO § 8 Legal Analysis... This may take several minutes."
    ):
        try:
            result_update = claims_clarity_agent(state)
            clarity_result = (
                result_update.get("claims_clarity_results") if result_update else None
            )
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            import traceback

            st.code(traceback.format_exc())
            clarity_result = None

    if clarity_result and clarity_result.get("status") == "SUCCESS":
        st.success("✅ Analysis Complete!")

        # Overall metrics
        overall = clarity_result.get("overall", {})

        st.markdown("---")
        st.subheader("📊 Overall Assessment")

        col1, col2, col3 = st.columns(3)
        with col1:
            decision = overall.get("examination_decision", "N/A")
            color = (
                "🟢"
                if decision == "GRANT"
                else "🟡"
                if decision == "FURTHER_EXAMINATION"
                else "🔴"
            )
            st.metric("Decision", f"{color} {decision}")
        with col2:
            risk = overall.get("risk_level", "N/A")
            st.metric("Risk Level", risk)
        with col3:
            issues = len(overall.get("critical_issues", []))
            st.metric("Critical Issues", issues)

        # Summary
        st.markdown("### 📝 Summary")
        st.info(overall.get("summary", "No summary available."))

        # Detailed tabs
        st.markdown("---")
        st.subheader("Detailed Analysis")

        tab_enb, tab_clr, tab_sup, tab_rpt = st.tabs(
            ["📐 Enablement", "🔍 Clarity", "📝 Support", "📄 Formal Report"]
        )

        with tab_enb:
            enb = clarity_result.get("enablement", {})
            st.markdown(f"**Status:** `{enb.get('status', 'N/A')}`")
            st.markdown(f"**Confidence:** {enb.get('confidence', 'N/A')}")
            st.progress(
                enb.get("reproducibility_score", 0),
                text=f"Reproducibility: {enb.get('reproducibility_score', 0):.1%}",
            )

            if enb.get("issues"):
                st.markdown("**🚨 Issues:**")
                for issue in enb["issues"]:
                    st.markdown(f"- {issue}")

            if enb.get("missing_elements"):
                st.markdown("**❌ Missing Elements:**")
                for elem in enb["missing_elements"]:
                    st.markdown(f"- {elem}")

            if enb.get("technical_deficiencies"):
                st.markdown("**⚠️ Technical Deficiencies:**")
                for defic in enb["technical_deficiencies"]:
                    st.markdown(f"- {defic}")

        with tab_clr:
            clr = clarity_result.get("clarity", {})
            st.markdown(f"**Status:** `{clr.get('status', 'N/A')}`")
            st.markdown(f"**Confidence:** {clr.get('confidence', 'N/A')}")
            st.progress(
                clr.get("clarity_score", 0),
                text=f"Clarity Score: {clr.get('clarity_score', 0):.1%}",
            )

            if clr.get("issues"):
                st.markdown("**🚨 Issues:**")
                for issue in clr["issues"]:
                    st.markdown(f"- {issue}")

            if clr.get("vague_terms"):
                st.markdown("**🌫️ Vague Terms:**")
                for term in clr["vague_terms"]:
                    st.markdown(f"- `{term}`")

            if clr.get("undefined_terms"):
                st.markdown("**❓ Undefined Terms:**")
                for term in clr["undefined_terms"]:
                    st.markdown(f"- `{term}`")

            if clr.get("ambiguous_phrases"):
                st.markdown("**🔮 Ambiguous Phrases:**")
                for phrase in clr["ambiguous_phrases"]:
                    st.markdown(f'- "{phrase}"')

        with tab_sup:
            sup = clarity_result.get("support", {})
            st.markdown(f"**Status:** `{sup.get('status', 'N/A')}`")
            st.markdown(f"**Confidence:** {sup.get('confidence', 'N/A')}")
            st.progress(
                sup.get("support_score", 0),
                text=f"Support Score: {sup.get('support_score', 0):.1%}",
            )

            if sup.get("issues"):
                st.markdown("**🚨 Issues:**")
                for issue in sup["issues"]:
                    st.markdown(f"- {issue}")

            if sup.get("unsupported_elements"):
                st.markdown("**❌ Unsupported Elements:**")
                for elem in sup["unsupported_elements"]:
                    st.markdown(f"- {elem}")

            if sup.get("broader_than_description"):
                st.markdown("**📏 Broader Than Description:**")
                for item in sup["broader_than_description"]:
                    st.markdown(f"- {item}")

            if sup.get("missing_embodiments"):
                st.markdown("**🔧 Missing Embodiments:**")
                for emb in sup["missing_embodiments"]:
                    st.markdown(f"- {emb}")

        with tab_rpt:
            report = clarity_result.get("formal_report", "")
            if report:
                st.markdown(report)
            else:
                st.info("No formal report was generated.")

        # Recommendations
        recs = overall.get("recommendations", [])
        if recs:
            st.markdown("---")
            st.subheader("🎯 Recommendations")
            for rec in recs:
                st.markdown(f"- {rec}")

        # Show output files
        st.markdown("---")
        st.subheader("📁 Output Files")
        st.markdown(f"Saved to: `{OUTPUT_DIR}`")

        if OUTPUT_DIR.exists():
            files = [f.name for f in OUTPUT_DIR.iterdir() if f.is_file()]
            if files:
                st.code("\n".join(files))
            else:
                st.caption("No output files yet")

    elif clarity_result and clarity_result.get("status") == "ERROR":
        st.error(f"❌ Analysis Error: {clarity_result.get('error', 'Unknown error')}")
        if clarity_result.get("message"):
            st.info(clarity_result["message"])
    else:
        st.warning("No results returned from analysis.")

st.markdown("---")
st.caption("Patent Analysis Tool — Agent 4: Claims Clarity (NIPO § 8)")
