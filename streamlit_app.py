import os
import tempfile
import streamlit as st
from pathlib import Path

from graph_workflow import app_graph
from graph_state import GraphState
from agents.agent2_ai_generated_detection.ai_generated_detection_agent import (
    ai_generated_detection_agent,
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


def save_upload(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    ext = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name


if st.button("🚀 Run Extraction Graph", type="primary", use_container_width=True):
    if not any([desc_file, claims_file, drawings_file]):
        st.error("Please upload at least one document.")
    else:
        # Clear any previous results
        st.session_state.run_count += 1

        with st.spinner("Saving files temporarily..."):
            desc_path = save_upload(desc_file)
            claims_path = save_upload(claims_file)
            drawings_path = save_upload(drawings_file)

        # Debug info
        st.info(
            f"Processing: Desc={desc_file.name if desc_file else None}, Claims={claims_file.name if claims_file else None}, Drawings={drawings_file.name if drawings_file else None}"
        )

        initial_state: GraphState = {
            "description_path": desc_path,
            "claims_path": claims_path,
            "drawings_path": drawings_path,
            "description_text": None,
            "claims_text": None,
            "drawings_text": None,
            "claims_extracted_from_description": False,
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

        # Clean up temp files
        for path in [desc_path, claims_path, drawings_path]:
            if path and os.path.exists(path):
                os.unlink(path)

        # Show where claims came from
        if claims_file:
            st.caption("Claims source: Uploaded claims file")
        elif final_state.get("claims_text"):
            st.caption("Claims source: Extracted from description document")
        else:
            st.caption("Claims source: None found")

        if final_state.get("status") == "ERROR":
            st.error(f"Graph execution halted: {final_state.get('error_message')}")

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
        else:
            st.success("✅ Graph executed successfully!")

            # Run AI Detection independently
            ai_result = None
            try:
                with st.spinner("🤖 Running AI Generation Detection..."):
                    ai_state_update = ai_generated_detection_agent(final_state)
                    if ai_state_update:
                        final_state.update(ai_state_update)
                        ai_result = ai_state_update.get("ai_detection_results")
            except Exception as ai_e:
                st.warning(f"AI Detection encountered an error: {ai_e}")

            st.subheader("Graph Output State")

            claims_from_desc = final_state.get(
                "claims_extracted_from_description", False
            )

            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "Description Only" if claims_from_desc else "Description Text",
                    "Claims Text",
                    "Drawings Text",
                    "🤖 AI Generation Detection",
                ]
            )

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
                        # Save description_only.md
                        with open("description_only.md", "w", encoding="utf-8") as f:
                            f.write(txt)
                        st.caption("Saved to: description_only.md")
                else:
                    st.info("No description text extracted.")

            with tab2:
                txt = final_state.get("claims_text")
                if txt:
                    st.text_area("Extracted Claims", value=txt, height=400)
                    if claims_from_desc:
                        # Save claims.md
                        with open("claims.md", "w", encoding="utf-8") as f:
                            f.write(txt)
                        st.caption("Saved to: claims.md")
                else:
                    st.info("No claims text extracted.")

            with tab3:
                txt = final_state.get("drawings_text")
                if txt:
                    st.text_area("Extracted Drawings", value=txt, height=400)
                else:
                    st.info("No drawings text extracted.")

            with tab4:
                if ai_result and ai_result.get("status") == "SUCCESS":
                    st.subheader("📊 AI Generation Detection")

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
                            "YES ⚠️"
                            if ai_result.get("is_likely_ai_generated")
                            else "NO ✓",
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
                            (
                                "Fingerprint",
                                feature_scores.get("fingerprint", 0),
                                "30%",
                            ),
                            (
                                "Anchor",
                                feature_scores.get("anchor_similarity", 0),
                                "40%",
                            ),
                            (
                                "Hallucination",
                                feature_scores.get("hallucination", 0),
                                "20%",
                            ),
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

                    with open("ai_detection_result.json", "w", encoding="utf-8") as f:
                        json.dump(ai_result, f, indent=2, ensure_ascii=False)
                    st.caption("Saved to: ai_detection_result.json")

                elif ai_result and ai_result.get("status") == "ERROR":
                    st.error(
                        f"AI Detection failed: {ai_result.get('error', 'Unknown error')}"
                    )
                else:
                    st.info("No AI detection results available.")
