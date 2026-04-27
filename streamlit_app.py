import os
import streamlit as st
from pathlib import Path

from graph_workflow import app_graph
from graph_state import GraphState
from agents.agent2b_ai_generated_document.ai_generated_detection_agent import (
    ai_generated_detection_agent,
)
from agents.agent4_claims_clarity.claims_clarity_agent import (
    claims_clarity_agent,
)

st.set_page_config(page_title="LangGraph Patent Analyzer", page_icon="🕸️", layout="wide")

st.title("🕸️ LangGraph Patent Analyzer: Step 1")
st.markdown(
    "Testing the central LangGraph state orchestration for document extraction."
)

# Session state for tracking current upload to prevent stale data
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

st.subheader("1. Upload Documents")
col1, col2, col3 = st.columns(3)
with col1:
    desc_file = st.file_uploader(
        "Description PDF",
        type=["pdf", "docx", "png"],
        key=f"desc_{st.session_state.run_count}",
    )
with col2:
    claims_file = st.file_uploader(
        "Claims PDF",
        type=["pdf", "docx", "png"],
        key=f"claims_{st.session_state.run_count}",
    )
with col3:
    drawings_file = st.file_uploader(
        "Drawings PDF",
        type=["pdf", "docx", "png"],
        key=f"draw_{st.session_state.run_count}",
    )


# Create input/output directories for document processing
INPUT_DIR = Path("input_pdf_documents")
OUTPUT_DIR = Path("output_text_documents")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def clear_directory(directory: Path):
    """Remove all files from a directory."""
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")


def save_upload(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    # Save to input directory with original filename
    save_path = INPUT_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(save_path)


if st.button("🚀 Run Extraction Graph", type="primary", use_container_width=True):
    if not any([desc_file, claims_file, drawings_file]):
        st.error("Please upload at least one document.")
    else:
        # Clear old files from both directories
        clear_directory(INPUT_DIR)
        clear_directory(OUTPUT_DIR)

        # Clear any previous results
        st.session_state.run_count += 1

        with st.spinner("Saving uploaded files to input_pdf_documents..."):
            desc_path = save_upload(desc_file)
            claims_path = save_upload(claims_file)
            drawings_path = save_upload(drawings_file)

        st.info(
            f"📂 Input files saved to: {INPUT_DIR}\n"
            f"   Description: {desc_file.name if desc_file else 'None'}\n"
            f"   Claims: {claims_file.name if claims_file else 'None'}\n"
            f"   Drawings: {drawings_file.name if drawings_file else 'None'}"
        )

        initial_state: GraphState = {
            "description_path": desc_path,
            "claims_path": claims_path,
            "drawings_path": drawings_path,
            "description_text": None,
            "claims_text": None,
            "drawings_text": None,
            "claims_extracted_from_description": False,
            "ai_detection_results": None,
            "claims_clarity_results": None,
            "status": "INITIALIZED",
            "error_message": None,
            "final_report": None,
            "proposal_letter": None,
        }

        import json
        from copy import deepcopy
        from datetime import datetime

        with st.spinner("Executing LangGraph Extractor Node and writing log..."):
            final_state = deepcopy(initial_state)

            log_path = "graph_agents_states.md"

            def truncate_dict(d):
                """Helper to truncate large strings so they don't bloat the markdown log"""
                if not d or not isinstance(d, dict):
                    return {}
                td = {}
                for k, v in d.items():
                    if isinstance(v, str) and len(v) > 500:
                        td[k] = f"<Text truncated... Length: {len(v)} characters>"
                    else:
                        td[k] = v
                return td

            with open(log_path, "w", encoding="utf-8") as f:
                f.write("# LangGraph Execution Trace\n")
                f.write(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## 🟢 Start State (Input)\n```json\n")
                f.write(json.dumps(truncate_dict(final_state), indent=2))
                f.write("\n```\n\n")

                st.info(
                    f"📝 Agent execution states are being logged securely to `{log_path}`"
                )

                step = 1
                for event in app_graph.stream(initial_state):
                    for node_name, state_update in event.items():
                        # Write the Agent Updates to log
                        f.write(
                            f"## ⚙️ Step {step}: Agent `{node_name}` Updates\n```json\n"
                        )
                        f.write(json.dumps(truncate_dict(state_update), indent=2))
                        f.write("\n```\n\n")

                        # Accumulate LangGraph updates into our final state wrapper for downstream tabs
                        if state_update and isinstance(state_update, dict):
                            final_state.update(state_update)
                        step += 1

                # End state
                f.write("## 🏁 End State / Final State\n```json\n")
                f.write(json.dumps(truncate_dict(final_state), indent=2))
                f.write("\n```\n\n")

        # Files are kept in uploads/ directory for debugging
        # Show where claims came from
        if claims_file:
            st.caption("Claims source: Uploaded claims file")
        elif final_state.get("claims_text"):
            st.caption("Claims source: Extracted from description document")
        else:
            st.caption("Claims source: None found")

        # Show extraction results regardless of status
        st.subheader("Extracted Documents")

        claims_from_desc = final_state.get("claims_extracted_from_description", False)
        status = final_state.get("status", "")
        has_error = status == "ERROR"
        has_warning = status == "WARNING"

        if has_error:
            st.error(
                f"⚠️ {final_state.get('error_message', 'An error occurred during processing')}"
            )

            # Display the formal legal report if available
            report = final_state.get("final_report")
            if report:
                st.markdown("---")
                st.subheader("📝 Official Analytical Report")
                st.markdown(report)
                st.markdown("---")

            # Display the proposal letter if available
            proposal = final_state.get("proposal_letter")
            if proposal:
                st.subheader("✉️ Drafted Proposal Letter")
                st.info(
                    "The following letter is a proposed draft for the examiner to send to the applicant."
                )
                st.markdown(proposal)
                st.markdown("---")
        elif has_warning:
            st.warning(
                f"⚠️ {final_state.get('error_message', 'A warning occurred during processing')}"
            )
        else:
            st.success("✅ Graph executed successfully!")

        # Save extracted text to output_text_documents
        desc_text = final_state.get("description_text", "") or ""
        claims_text = final_state.get("claims_text", "") or ""
        drawings_text = final_state.get("drawings_text", "") or ""

        if desc_text:
            with open(OUTPUT_DIR / "description.md", "w", encoding="utf-8") as f:
                f.write(desc_text)
        if claims_text:
            with open(OUTPUT_DIR / "claims.md", "w", encoding="utf-8") as f:
                f.write(claims_text)
        if drawings_text:
            with open(OUTPUT_DIR / "drawings.md", "w", encoding="utf-8") as f:
                f.write(drawings_text)

        # Show directory contents
        st.markdown("---")
        col_dir1, col_dir2 = st.columns(2)
        with col_dir1:
            st.markdown(f"**📂 Input PDF Documents (`{INPUT_DIR}`):**")
            input_files = [f.name for f in INPUT_DIR.iterdir() if f.is_file()]
            if input_files:
                st.code("\n".join(input_files))
            else:
                st.caption("No files")
        with col_dir2:
            st.markdown(f"**📄 Output Text Documents (`{OUTPUT_DIR}`):**")
            output_files = [f.name for f in OUTPUT_DIR.iterdir() if f.is_file()]
            if output_files:
                st.code("\n".join(output_files))
            else:
                st.caption("No files")

        # Always show extraction tabs
        st.markdown("---")
        st.subheader("Extracted Text")
        tab1, tab2, tab3 = st.tabs(["📑 Description", "⚖️ Claims", "🖼️ Drawings"])

        with tab1:
            txt = final_state.get("description_text")
            if txt:
                label = (
                    "Description Only (claims removed)"
                    if claims_from_desc
                    else "Extracted Description"
                )
                st.text_area(label, value=txt, height=400)
                if claims_from_desc:
                    st.info(
                        "Claims section was removed from description and placed in Claims tab"
                    )
                st.caption(f"Saved to: {OUTPUT_DIR / 'description.md'}")
            else:
                st.warning(
                    "No description text extracted. Check if file was uploaded correctly."
                )

        with tab2:
            txt = final_state.get("claims_text")
            if txt:
                st.text_area("Extracted Claims", value=txt, height=400)
                st.caption(f"Saved to: {OUTPUT_DIR / 'claims.md'}")
            else:
                st.warning(
                    "No claims text extracted. If you uploaded a claims file, the extraction may have failed. If not, claims will be extracted from the description if present."
                )

        with tab3:
            txt = final_state.get("drawings_text")
            if txt:
                st.text_area("Extracted Drawings", value=txt, height=400)
                st.caption(f"Saved to: {OUTPUT_DIR / 'drawings.md'}")
            else:
                st.info(
                    "No drawings text extracted. Upload a drawings file to see extraction results."
                )

        # Run AI Detection independently (always run, even on error)
        st.markdown("---")
        st.subheader("🤖 AI Generation Detection")

        ai_result = None
        try:
            with st.spinner("Running AI Generation Detection..."):
                ai_state_update = ai_generated_detection_agent(final_state)
                if ai_state_update:
                    final_state.update(ai_state_update)
                    ai_result = ai_state_update.get("ai_detection_results")
        except Exception as ai_e:
            st.warning(f"AI Detection encountered an error: {ai_e}")

        if ai_result and ai_result.get("status") == "SUCCESS":
            # Brief summary at top
            brief = ai_result.get("brief_summary", "")
            if brief:
                st.info(brief)

            # Full detailed summary
            summary = ai_result.get("summary", "")
            if summary:
                with st.expander("📖 View Full Analysis Report", expanded=True):
                    st.markdown(summary)

            # Key metrics
            st.markdown("### 📈 Key Metrics")
            colA, colB = st.columns(2)
            with colA:
                st.metric(
                    "AI Generated",
                    "YES ⚠️" if ai_result.get("is_likely_ai_generated") else "NO ✓",
                )
                st.metric("Risk Level", ai_result.get("risk_level", "UNKNOWN"))
            with colB:
                st.metric(
                    "Confidence Score",
                    f"{ai_result.get('confidence_score', 0):.1%}",
                )
                st.metric("Main Driver", "Anchor Comparison")

            # Feature Scores
            st.markdown("### 📊 Feature Scores Breakdown")
            feature_scores = ai_result.get("feature_scores", {})
            if feature_scores:
                score_cols = st.columns(4)
                score_data = [
                    ("Fingerprint", feature_scores.get("fingerprint", 0), "30%"),
                    ("Anchor", feature_scores.get("anchor_similarity", 0), "40%"),
                    ("Hallucination", feature_scores.get("hallucination", 0), "20%"),
                    ("Drawing", feature_scores.get("drawing", 0), "10%"),
                ]
                for i, (name, score, weight) in enumerate(score_data):
                    with score_cols[i]:
                        st.metric(f"{name} ({weight})", f"{score:.1%}")

            # Recommendations
            recommendations = ai_result.get("recommendations", [])
            if recommendations:
                st.markdown("### 🎯 Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

            # Technical details in expander
            st.markdown("### 🔍 Technical Details")
            with st.expander("View Raw Analysis Data"):
                st.json(ai_result.get("detailed_analysis", {}))

            # Save results
            import json

            AI_DETECTION_DIR = Path("agents/agent2b_ai_generated_document")
            AI_DETECTION_DIR.mkdir(exist_ok=True)

            with open(
                AI_DETECTION_DIR / "ai_detection_result.json", "w", encoding="utf-8"
            ) as f:
                json.dump(ai_result, f, indent=2, ensure_ascii=False)
            st.caption(f"Saved to: {AI_DETECTION_DIR / 'ai_detection_result.json'}")

        elif ai_result and ai_result.get("status") == "ERROR":
            st.error(f"AI Detection failed: {ai_result.get('error', 'Unknown error')}")
        else:
            st.info("No AI detection results available.")

        # ========================================================================
        # AGENT 4: CLAIMS CLARITY ANALYSIS (Continuation of Pipeline)
        # ========================================================================
        st.markdown("---")
        st.subheader("⚖️ Agent 4: Claims Clarity Analysis")
        st.caption(
            "🔁 CONTINUATION: This agent reads extracted documents from above and performs NIPO § 8 legal analysis."
        )

        # Check if extracted files exist
        has_extracted_files = (
            (OUTPUT_DIR / "description.md").exists()
            or final_state.get("description_text")
        ) and ((OUTPUT_DIR / "claims.md").exists() or final_state.get("claims_text"))

        if not has_extracted_files:
            st.warning(
                "⚠️ No extracted documents found. Please run Steps 1-3 (Document Extraction) above first."
            )
        else:
            if st.button(
                "🔍 Run Claims Clarity Analysis",
                type="secondary",
                use_container_width=True,
            ):
                with st.spinner(
                    "Running NIPO § 8 Legal Analysis (Enablement, Clarity, Support)..."
                ):
                    try:
                        clarity_state_update = claims_clarity_agent(final_state)
                        if clarity_state_update:
                            final_state.update(clarity_state_update)
                            clarity_result = clarity_state_update.get(
                                "claims_clarity_results"
                            )
                        else:
                            clarity_result = None
                    except Exception as clarity_e:
                        st.error(f"Claims Clarity Analysis failed: {clarity_e}")
                        clarity_result = None

                if clarity_result and clarity_result.get("status") == "SUCCESS":
                    # Show overall assessment
                    overall = clarity_result.get("overall", {})

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Examination Decision",
                            overall.get("examination_decision", "N/A"),
                        )
                    with col2:
                        st.metric("Risk Level", overall.get("risk_level", "N/A"))
                    with col3:
                        critical_count = len(overall.get("critical_issues", []))
                        st.metric("Critical Issues", critical_count)

                    # Summary
                    st.markdown("### 📋 Summary")
                    st.write(overall.get("summary", "No summary available."))

                    # Create tabs for detailed analysis
                    tab_enb, tab_clr, tab_sup, tab_report = st.tabs(
                        [
                            "📊 Enablement",
                            "🔍 Clarity",
                            "📝 Support",
                            "📄 Formal Report",
                        ]
                    )

                    with tab_enb:
                        enb = clarity_result.get("enablement", {})
                        st.markdown(f"**Status:** {enb.get('status', 'N/A')}")
                        st.markdown(f"**Confidence:** {enb.get('confidence', 'N/A')}")
                        st.markdown(
                            f"**Reproducibility Score:** {enb.get('reproducibility_score', 0):.1%}"
                        )

                        if enb.get("issues"):
                            st.markdown("**Issues:**")
                            for issue in enb["issues"]:
                                st.markdown(f"- {issue}")

                        if enb.get("missing_elements"):
                            st.markdown("**Missing Elements:**")
                            for elem in enb["missing_elements"]:
                                st.markdown(f"- {elem}")

                    with tab_clr:
                        clr = clarity_result.get("clarity", {})
                        st.markdown(f"**Status:** {clr.get('status', 'N/A')}")
                        st.markdown(f"**Confidence:** {clr.get('confidence', 'N/A')}")
                        st.markdown(
                            f"**Clarity Score:** {clr.get('clarity_score', 0):.1%}"
                        )

                        if clr.get("issues"):
                            st.markdown("**Issues:**")
                            for issue in clr["issues"]:
                                st.markdown(f"- {issue}")

                        if clr.get("vague_terms"):
                            st.markdown("**Vague Terms:**")
                            for term in clr["vague_terms"]:
                                st.markdown(f"- {term}")

                    with tab_sup:
                        sup = clarity_result.get("support", {})
                        st.markdown(f"**Status:** {sup.get('status', 'N/A')}")
                        st.markdown(f"**Confidence:** {sup.get('confidence', 'N/A')}")
                        st.markdown(
                            f"**Support Score:** {sup.get('support_score', 0):.1%}"
                        )

                        if sup.get("issues"):
                            st.markdown("**Issues:**")
                            for issue in sup["issues"]:
                                st.markdown(f"- {issue}")

                    with tab_report:
                        report = clarity_result.get("formal_report", "")
                        if report:
                            st.markdown(report)
                        else:
                            st.info("No formal report generated.")

                    # Recommendations
                    recs = overall.get("recommendations", [])
                    if recs:
                        st.markdown("### 🎯 Recommendations")
                        for rec in recs:
                            st.markdown(f"- {rec}")

                    # Show output files
                    st.markdown("---")
                    report_dir = Path("output_analysis_reports")
                    st.markdown(f"**📄 Analysis Reports saved to:** `{report_dir}`")
                    if report_dir.exists():
                        report_files = [
                            f.name for f in report_dir.iterdir() if f.is_file()
                        ]
                        if report_files:
                            st.code("\n".join(report_files))

                elif clarity_result and clarity_result.get("status") == "ERROR":
                    st.error(f"❌ {clarity_result.get('error', 'Unknown error')}")
                    st.info(clarity_result.get("message", ""))
                else:
                    st.info("No claims clarity results available.")
