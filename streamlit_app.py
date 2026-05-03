import os
import json
import streamlit as st
from pathlib import Path
from copy import deepcopy
from datetime import datetime
from collections import defaultdict

from graph_workflow import app_graph
from graph_state import GraphState, create_initial_state
from agents.agent2b_ai_generated_document.ai_generated_detection_agent import (
    ai_generated_detection_agent,
)
from agents.agent3b_claims_founded.claims_founded_agent import ClaimsFoundedAgent
from agents.agent4a_claims_clarity.claims_clarity_agent import ClaimsClarityAgent
from agents.agent4b_claims_unity.claims_unity_agent import ClaimsUnityAgent
from agents.agent4c_claims_antecedent.claims_antecedent_agent import (
    ClaimsAntecedentAgent,
)
from agents.agent4_claims_legal_analyse.claims_legal_analyse_agent import (
    ClaimsLegalAnalysisAgent,
)
from pipeline import run_full_analysis

st.set_page_config(page_title="Patent Analyzer", page_icon="🕸️", layout="wide")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "final_state" not in st.session_state:
    st.session_state.final_state = None

if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = {}

if "is_running" not in st.session_state:
    st.session_state.is_running = False

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# ============================================================================
# CONSTANTS
# ============================================================================
INPUT_DIR = Path("input_pdf_documents")
OUTPUT_DIR = Path("output_text_documents")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def clear_directory(directory: Path):
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")


def save_upload(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    save_path = INPUT_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(save_path)


def truncate_dict(d):
    if not d or not isinstance(d, dict):
        return {}
    td = {}
    for k, v in d.items():
        if isinstance(v, str) and len(v) > 500:
            td[k] = f"<Text truncated... Length: {len(v)} characters>"
        else:
            td[k] = v
    return td


def reset_pipeline():
    st.session_state.final_state = None
    st.session_state.pipeline_status = {}
    st.session_state.is_running = False
    st.session_state.uploaded_files = {}
    clear_directory(INPUT_DIR)
    clear_directory(OUTPUT_DIR)


# ============================================================================
# HEADER
# ============================================================================
st.title("🕸️ Patent Analyzer")
st.markdown(
    "Complete patent analysis pipeline: extraction, detection, and legal analysis."
)

# ============================================================================
# SIDEBAR - CONTROLS
# ============================================================================
with st.sidebar:
    st.header("📂 Upload Documents")

    desc_file = st.file_uploader(
        "Description PDF",
        type=["pdf", "docx", "png"],
        key="desc_uploader",
    )
    claims_file = st.file_uploader(
        "Claims PDF",
        type=["pdf", "docx", "png"],
        key="claims_uploader",
    )
    drawings_file = st.file_uploader(
        "Drawings PDF",
        type=["pdf", "docx", "png"],
        key="drawings_uploader",
    )

    st.markdown("---")

    if st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True):
        if not any([desc_file, claims_file, drawings_file]):
            st.error("Please upload at least one document.")
        else:
            reset_pipeline()

            # Save files immediately
            desc_path = save_upload(desc_file)
            claims_path = save_upload(claims_file)
            drawings_path = save_upload(drawings_file)

            st.session_state.uploaded_files = {
                "desc": desc_path,
                "claims": claims_path,
                "drawings": drawings_path,
            }
            st.session_state.is_running = True
            st.rerun()

    if st.button("🔄 Reset", use_container_width=True):
        reset_pipeline()
        st.rerun()

    st.markdown("---")
    st.caption("Pipeline Status:")
    for step, status in st.session_state.pipeline_status.items():
        if status is True:
            icon = "✅"
        elif status is False or status is None:
            icon = "⬜"
        else:
            icon = "⚠️"
        st.caption(f"{icon} {step.replace('_', ' ').title()}")

# ============================================================================
# PIPELINE EXECUTION
# ============================================================================
if st.session_state.is_running and not st.session_state.final_state:
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        files = st.session_state.uploaded_files
        desc_path = files.get("desc")
        claims_path = files.get("claims")
        drawings_path = files.get("drawings")

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
            "claims_unity_results": None,
            "claims_antecedent_results": None,
            "claims_founded_results": None,
            "claims_legal_analysis_results": None,
            "cpc_classes": None,
            "cpc_classification": None,
            "metadata": {},
            "processing_warnings": [],
            "status": "INITIALIZED",
            "error_message": None,
            "final_report": None,
            "proposal_letter": None,
        }

        final_state = deepcopy(initial_state)

        # Step 1: Document Extraction (LangGraph)
        status_text.text("Step 1/8: Extracting text from documents...")
        progress_bar.progress(10)

        log_path = "graph_agents_states.md"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("# LangGraph Execution Trace\n")
            f.write(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Start State (Input)\n```json\n")
            f.write(json.dumps(truncate_dict(final_state), indent=2))
            f.write("\n```\n\n")

            step = 1
            for event in app_graph.stream(initial_state):
                for node_name, state_update in event.items():
                    f.write(f"## Step {step}: Agent `{node_name}` Updates\n```json\n")
                    f.write(json.dumps(truncate_dict(state_update), indent=2))
                    f.write("\n```\n\n")

                    if state_update and isinstance(state_update, dict):
                        final_state.update(state_update)
                    step += 1

            f.write("## End State / Final State\n```json\n")
            f.write(json.dumps(truncate_dict(final_state), indent=2))
            f.write("\n```\n\n")

        # Save extracted text to files
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

        st.session_state.pipeline_status["extraction"] = True

        # Check if extraction halted (no claims)
        if final_state.get("status") == "ERROR":
            st.session_state.final_state = final_state
            st.session_state.is_running = False
            st.rerun()

        # Step 2: Claims Founded (Structural Analysis)
        if claims_text:
            status_text.text("Step 2/8: Analyzing claim structure...")
            progress_bar.progress(20)
            try:
                agent = ClaimsFoundedAgent()
                final_state = agent.process(final_state)
                st.session_state.pipeline_status["claims_founded"] = True
            except Exception as e:
                st.session_state.pipeline_status["claims_founded"] = f"Error: {e}"

        # Step 3: AI Detection
        status_text.text("Step 3/8: Running AI generation detection...")
        progress_bar.progress(35)
        try:
            ai_state_update = ai_generated_detection_agent(final_state)
            if ai_state_update:
                final_state.update(ai_state_update)
            st.session_state.pipeline_status["ai_detection"] = True
        except Exception as e:
            st.session_state.pipeline_status["ai_detection"] = f"Error: {e}"

        # Step 4: Claims Clarity
        if claims_text and final_state.get("status") != "ERROR":
            status_text.text("Step 4/8: Claims clarity analysis (NIPO 8)...")
            progress_bar.progress(50)
            try:
                agent = ClaimsClarityAgent()
                final_state = agent.process(final_state)
                st.session_state.pipeline_status["clarity"] = True
            except Exception as e:
                st.session_state.pipeline_status["clarity"] = f"Error: {e}"

        # Step 5: Claims Unity
        if claims_text and final_state.get("status") != "ERROR":
            status_text.text("Step 5/8: Claims unity analysis (NIPO 10)...")
            progress_bar.progress(60)
            try:
                agent = ClaimsUnityAgent()
                final_state = agent.process(final_state)
                st.session_state.pipeline_status["unity"] = True
            except Exception as e:
                st.session_state.pipeline_status["unity"] = f"Error: {e}"

        # Step 6: Antecedent Basis
        if claims_text and final_state.get("status") != "ERROR":
            status_text.text("Step 6/8: Antecedent basis analysis...")
            progress_bar.progress(75)
            try:
                agent = ClaimsAntecedentAgent()
                final_state = agent.process(final_state)
                st.session_state.pipeline_status["antecedent"] = True
            except Exception as e:
                st.session_state.pipeline_status["antecedent"] = f"Error: {e}"

        # Step 7: Comprehensive Legal Analysis
        if claims_text and final_state.get("status") != "ERROR":
            status_text.text("Step 7/8: Legal synthesis...")
            progress_bar.progress(90)
            try:
                agent = ClaimsLegalAnalysisAgent()
                final_state = agent.process(final_state)
                st.session_state.pipeline_status["legal"] = True
            except Exception as e:
                st.session_state.pipeline_status["legal"] = f"Error: {e}"

        # Done
        progress_bar.progress(100)
        status_text.text("Complete!")
        st.session_state.final_state = final_state
        st.session_state.is_running = False
        st.success("Analysis complete! View results in the tabs below.")

    except Exception as e:
        st.session_state.last_error = str(e)
        st.session_state.is_running = False
        st.error(f"Pipeline failed: {e}")

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================
final_state = st.session_state.final_state

(
    tab_upload,
    tab_extract,
    tab_founded,
    tab_ai,
    tab_clarity,
    tab_unity,
    tab_antecedent,
    tab_legal,
    tab_classification,
    tab_status,
) = st.tabs(
    [
        "📤 Upload",
        "📄 Extraction",
        "🏗️ Claims Structure",
        "🤖 AI Detection",
        "⚖️ Clarity",
        "🔗 Unity",
        "🔗 Antecedent",
        "📊 Legal",
        "🏷️ Classification",
        "📋 Status",
    ]
)

# --- TAB 1: UPLOAD ---
with tab_upload:
    st.header("Document Upload")
    st.info(
        "Use the sidebar to upload your patent documents and run the analysis pipeline."
    )

    if desc_file:
        st.success(f"📑 Description: {desc_file.name}")
    if claims_file:
        st.success(f"⚖️ Claims: {claims_file.name}")
    if drawings_file:
        st.success(f"🖼️ Drawings: {drawings_file.name}")

    if not any([desc_file, claims_file, drawings_file]):
        st.warning("No documents uploaded yet.")

# --- TAB 2: EXTRACTION ---
with tab_extract:
    st.header("Document Extraction Results")

    if not final_state:
        st.info("Run the pipeline to see extraction results.")
    else:
        claims_from_desc = final_state.get("claims_extracted_from_description", False)
        status = final_state.get("status", "")

        if status == "ERROR":
            st.error(f"❌ {final_state.get('error_message', 'Extraction failed')}")
        elif status == "WARNING":
            st.warning(f"⚠️ {final_state.get('error_message', 'Warning')}")
        else:
            st.success("✅ Extraction successful")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Description",
                f"{len(final_state.get('description_text', '') or '')} chars",
            )
        with col2:
            st.metric(
                "Claims", f"{len(final_state.get('claims_text', '') or '')} chars"
            )
        with col3:
            st.metric(
                "Drawings", f"{len(final_state.get('drawings_text', '') or '')} chars"
            )

        if claims_from_desc:
            st.info("Claims were extracted from the description document.")

        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Description", "Claims", "Drawings"])
        with sub_tab1:
            txt = final_state.get("description_text")
            if txt:
                st.text_area(
                    "Extracted Description",
                    value=txt,
                    height=400,
                    label_visibility="collapsed",
                )
            else:
                st.warning("No description extracted.")
        with sub_tab2:
            txt = final_state.get("claims_text")
            if txt:
                st.text_area(
                    "Extracted Claims",
                    value=txt,
                    height=400,
                    label_visibility="collapsed",
                )
            else:
                st.warning("No claims extracted.")
        with sub_tab3:
            txt = final_state.get("drawings_text")
            if txt:
                st.text_area(
                    "Extracted Drawings",
                    value=txt,
                    height=400,
                    label_visibility="collapsed",
                )
            else:
                st.info("No drawings extracted.")

# --- TAB 3: CLAIMS FOUNDED ---
with tab_founded:
    st.header("Claims Structural Analysis")

    if not final_state:
        st.info("Run the pipeline to see structural analysis results.")
    else:
        founded_result = final_state.get("claims_founded_results")

        if founded_result and founded_result.get("status") == "SUCCESS":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Claims", founded_result.get("total_claims", 0))
            with col2:
                st.metric(
                    "Independent",
                    len(founded_result.get("independent_claims", [])),
                )
            with col3:
                st.metric(
                    "Dependent",
                    len(founded_result.get("dependent_claims", [])),
                )

            stats = founded_result.get("statistics", {})
            st.markdown(
                f"**Max Dependency Depth:** {stats.get('max_dependency_depth', 0)} | "
                f"**Avg Length:** {stats.get('avg_claim_length', 0)} chars"
            )

            # Display Dependency Graph
            graph_path = Path(
                "claims_analyse_reports/claims_founded/dependency_graph.html"
            )
            if graph_path.exists():
                st.markdown("### Dependency Graph")
                with open(graph_path, "r", encoding="utf-8") as f:
                    graph_html = f.read()
                st.components.v1.html(graph_html, height=600, scrolling=True)
            else:
                st.info("Dependency graph not generated yet.")

            issues = founded_result.get("issues", [])
            if issues:
                st.markdown("### Issues Found")
                for issue in issues:
                    icon = (
                        "🔴"
                        if issue["severity"] == "ERROR"
                        else "⚠️"
                        if issue["severity"] == "WARNING"
                        else "ℹ️"
                    )
                    st.markdown(f"{icon} **{issue['type']}** ({issue['severity']})")
                    st.caption(issue.get("description", ""))
            else:
                st.success("✅ No structural issues found.")

            tree = founded_result.get("dependency_tree", {})
            if tree:
                with st.expander("View Dependency Tree"):
                    st.json(tree)

            orphaned = founded_result.get("orphaned_claims", [])
            if orphaned:
                st.warning(
                    f"⚠️ Orphaned claims (never referenced): {', '.join(map(str, orphaned))}"
                )

            broken = founded_result.get("broken_dependencies", [])
            if broken:
                st.error("🔴 Broken Dependencies")
                for dep in broken:
                    st.markdown(
                        f"- Claim {dep['claim']} references missing claim {dep['missing_dependency']}"
                    )

            circular = founded_result.get("circular_dependencies", [])
            if circular:
                st.error("🔴 Circular Dependencies")
                st.markdown(f"Claims involved: {', '.join(map(str, circular))}")

            # Display Terminology Explanations
            st.markdown("---")
            st.markdown("### Understanding the Analysis")

            with st.expander("What are Circular Dependencies?"):
                st.markdown(
                    """
                    A **circular dependency** occurs when a claim references itself or creates a loop. 
                    For example, if Claim 2 says 'according to Claim 3' and Claim 3 says 'according to Claim 2', 
                    this creates an impossible circular reference. 
                    
                    Valid patents must have a clear hierarchical structure where dependent claims ultimately 
                    trace back to an independent claim without loops.
                    """
                )

            with st.expander("What are Orphaned Claims?"):
                st.markdown(
                    """
                    An **orphaned claim** is a dependent claim that is never referenced by any other claim. 
                    This is **completely normal** in most patents. 
                    
                    For example, if Claims 2-10 all reference Claim 1 (the independent claim) but no other 
                    claims reference Claims 2-10, then Claims 2-10 are 'orphaned' - they are terminal leaves 
                    in the dependency tree. 
                    
                    This is a valid and common structure known as a 'star-shaped' or 'fan-out' pattern.
                    """
                )

            with st.expander("What is Dependency Depth?"):
                st.markdown(
                    """
                    **Dependency depth** measures how many levels of dependency exist in the claim tree.
                    
                    For example:
                    - Claim 1 (independent) -> Claim 2 (depends on 1) = Depth 1
                    - Claim 1 -> Claim 2 -> Claim 3 (depends on 2) = Depth 2
                    
                    Most jurisdictions recommend keeping depth under 5 for clarity.
                    """
                )

        elif founded_result and founded_result.get("status") == "ERROR":
            st.error(f"❌ {founded_result.get('error', 'Unknown error')}")
        else:
            st.info("No structural analysis results available.")

# --- TAB 4: AI DETECTION ---
with tab_ai:
    st.header("AI Generation Detection")

    if not final_state:
        st.info("Run the pipeline to see AI detection results.")
    else:
        ai_result = final_state.get("ai_detection_results")

        if ai_result and ai_result.get("status") == "SUCCESS":
            brief = ai_result.get("brief_summary", "")
            if brief:
                st.info(brief)

            summary = ai_result.get("summary", "")
            if summary:
                with st.expander("📖 View Full Analysis Report", expanded=True):
                    st.markdown(summary)

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

            feature_scores = ai_result.get("feature_scores", {})
            if feature_scores:
                st.markdown("### 📊 Feature Scores Breakdown")
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

            recommendations = ai_result.get("recommendations", [])
            if recommendations:
                st.markdown("### 🎯 Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

            with st.expander("View Raw Analysis Data"):
                st.json(ai_result.get("detailed_analysis", {}))

        elif ai_result and ai_result.get("status") == "ERROR":
            st.error(f"AI Detection failed: {ai_result.get('error', 'Unknown error')}")
        else:
            st.info("No AI detection results available.")

# --- TAB 4: CLARITY ---
with tab_clarity:
    st.header("Claims Clarity Analysis (NIPO §8)")

    if not final_state:
        st.info("Run the pipeline to see clarity analysis results.")
    else:
        clarity_result = final_state.get("claims_clarity_results")

        if clarity_result and clarity_result.get("status") == "SUCCESS":
            overall = clarity_result.get("overall", {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Examination Decision", overall.get("examination_decision", "N/A")
                )
            with col2:
                st.metric("Risk Level", overall.get("risk_level", "N/A"))
            with col3:
                st.metric("Critical Issues", len(overall.get("critical_issues", [])))

            st.markdown(
                f"**Summary:** {overall.get('summary', 'No summary available.')}"
            )

            tab_enb, tab_clr, tab_sup, tab_report = st.tabs(
                ["Enablement", "Clarity", "Support", "Formal Report"]
            )

            with tab_enb:
                enb = clarity_result.get("enablement", {})
                st.markdown(f"**Status:** {enb.get('status', 'N/A')}")
                st.markdown(f"**Confidence:** {enb.get('confidence', 'N/A')}")
                st.markdown(
                    f"**Reproducibility Score:** {enb.get('reproducibility_score', 0):.1%}"
                )
                if enb.get("issues"):
                    for issue in enb["issues"]:
                        st.markdown(f"- {issue}")

            with tab_clr:
                clr = clarity_result.get("clarity", {})
                st.markdown(f"**Status:** {clr.get('status', 'N/A')}")
                st.markdown(f"**Confidence:** {clr.get('confidence', 'N/A')}")
                st.markdown(f"**Clarity Score:** {clr.get('clarity_score', 0):.1%}")
                if clr.get("issues"):
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
                st.markdown(f"**Support Score:** {sup.get('support_score', 0):.1%}")
                if sup.get("issues"):
                    for issue in sup["issues"]:
                        st.markdown(f"- {issue}")

            with tab_report:
                report = clarity_result.get("formal_report", "")
                if report:
                    st.markdown(report)
                else:
                    st.info("No formal report generated.")

            recs = overall.get("recommendations", [])
            if recs:
                st.markdown("### 🎯 Recommendations")
                for rec in recs:
                    st.markdown(f"- {rec}")

        elif clarity_result and clarity_result.get("status") == "ERROR":
            st.error(f"❌ {clarity_result.get('error', 'Unknown error')}")
        else:
            st.info("No clarity analysis results available.")

# --- TAB 5: UNITY ---
with tab_unity:
    st.header("Claims Unity Analysis (NIPO §10)")

    if not final_state:
        st.info("Run the pipeline to see unity analysis results.")
    else:
        unity_result = final_state.get("claims_unity_results")

        if unity_result and unity_result.get("status") == "SUCCESS":
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Conclusion", unity_result.get("conclusion", "N/A"))
            with col2:
                st.metric("Confidence", unity_result.get("confidence", "N/A"))

            st.markdown(f"**Status Reason:** {unity_result.get('status_reason', '')}")

            grouping = unity_result.get("grouping", [])
            if grouping:
                st.markdown("### Claim Grouping")
                for group in grouping:
                    st.markdown(f"**Group {group.get('group_no', 'N/A')}:**")
                    st.markdown(
                        f"- Representative: {', '.join(group.get('representative_independent_claims', []))}"
                    )
                    st.markdown(
                        f"- Subject Matter: {group.get('technical_subject_matter', '')}"
                    )

            common = unity_result.get("common_features", [])
            if common:
                st.markdown("### Common Features")
                for feat in common:
                    st.markdown(f"- {feat}")

            rec = unity_result.get("recommendation", "")
            if rec:
                st.markdown("### Recommendation")
                st.markdown(rec)

            if unity_result.get("conclusion") == "MULTIPLE_INVENTIONS":
                st.error("⚠️ Multiple inventions detected!")

        elif unity_result and unity_result.get("status") == "ERROR":
            st.error(f"❌ {unity_result.get('error', 'Unknown error')}")
        else:
            st.info("No unity analysis results available.")

# --- TAB 6: ANTECEDENT ---
with tab_antecedent:
    st.header("Claims Antecedent Basis Analysis")

    if not final_state:
        st.info("Run the pipeline to see antecedent analysis results.")
    else:
        antecedent_result = final_state.get("claims_antecedent_results")

        if antecedent_result and antecedent_result.get("status") == "SUCCESS":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Claims", antecedent_result.get("claim_count", 0))
            with col2:
                st.metric("Issues Found", antecedent_result.get("issues_found", 0))
            with col3:
                st.metric(
                    "Claims with Issues", antecedent_result.get("claims_with_issues", 0)
                )

            if antecedent_result.get("llm_reviewed"):
                st.info(
                    f"✅ LLM reviewed: {antecedent_result.get('llm_filtered_count', 0)} false positives filtered"
                )

            issues = antecedent_result.get("issues", [])
            if issues:
                st.markdown("### Issues by Claim")
                claim_issues = defaultdict(list)
                for issue in issues:
                    claim_issues[issue["claim_number"]].append(issue)

                for claim_num in sorted(claim_issues.keys()):
                    with st.expander(f"Claim {claim_num}"):
                        for issue in claim_issues[claim_num]:
                            st.markdown(f"**{issue['definite_reference']}**")
                            st.markdown(f"- Reasoning: {issue['reasoning']}")
                            st.markdown(f"- Confidence: {issue['confidence']}")
            else:
                st.success("No antecedent basis issues found.")

        elif antecedent_result and antecedent_result.get("status") == "ERROR":
            st.error(f"❌ {antecedent_result.get('error', 'Unknown error')}")
        else:
            st.info("No antecedent analysis results available.")

# --- TAB 7: LEGAL ---
with tab_legal:
    st.header("Comprehensive Legal Analysis")

    if not final_state:
        st.info("Run the pipeline to see legal analysis results.")
    else:
        legal_result = final_state.get("claims_legal_analysis_results")

        if legal_result and legal_result.get("status") == "SUCCESS":
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Overall Assessment", legal_result.get("overall_assessment", "N/A")
                )
            with col2:
                st.metric("Risk Level", legal_result.get("risk_level", "N/A"))

            if legal_result.get("summary"):
                st.markdown("### Summary")
                st.write(legal_result["summary"])

            certain_defects = legal_result.get("certain_defects_paragraph", "")
            if certain_defects:
                st.markdown("### Certain Defects and Observations")
                st.markdown(certain_defects)

            critical = legal_result.get("critical_issues", [])
            if critical:
                st.markdown("### Critical Issues")
                for issue in critical:
                    st.markdown(f"- {issue}")

            recommendations = legal_result.get("recommendations", [])
            if recommendations:
                st.markdown("### Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

            if legal_result.get("formal_report"):
                with st.expander("📄 Formal Report"):
                    st.markdown(legal_result["formal_report"])

        elif legal_result and legal_result.get("status") == "ERROR":
            st.error(f"❌ {legal_result.get('error', 'Unknown error')}")
        else:
            st.info("No legal analysis results available.")

# --- TAB 8: CLASSIFICATION ---
with tab_classification:
    st.header("CPC Classification")

    if not final_state:
        st.info("Run the pipeline to see CPC classification results.")
    else:
        cpc_classes = final_state.get("cpc_classes")
        cpc_full = final_state.get("cpc_classification")

        if cpc_classes or cpc_full:
            # Simple CPC list for downstream
            if cpc_classes:
                st.markdown("### 📋 Detected CPC Classes")
                for code in cpc_classes:
                    st.markdown(f"- **{code}**")

            # Full classification details
            if cpc_full and isinstance(cpc_full, dict):
                phase1 = cpc_full.get("phase1", {})
                phase2 = cpc_full.get("phase2", {})
                phase3 = cpc_full.get("phase3", [])
                phase4 = cpc_full.get("phase4", {})

                # Phase 1 summary
                if phase1:
                    st.markdown("---")
                    st.markdown("### 🔍 Phase 1: Technical Understanding")

                    strategy = phase1.get("classification_strategy", "N/A")
                    st.metric("Strategy", strategy)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Technical Object**")
                        st.caption(phase1.get("technical_object", "N/A"))
                        st.markdown("**System Context**")
                        st.caption(phase1.get("system_context", "N/A"))
                    with col2:
                        st.markdown("**Core Function**")
                        st.caption(phase1.get("core_function", "N/A"))
                        st.markdown("**Problem Solved**")
                        st.caption(phase1.get("problem_solved", "N/A"))

                    # Essential terms
                    terms = phase1.get("essential_terms", [])
                    if terms:
                        st.markdown("**Essential Terms**")
                        term_cols = st.columns(min(len(terms), 4))
                        for i, term_data in enumerate(terms[:8]):
                            with term_cols[i % 4]:
                                term = (
                                    term_data.get("term", "")
                                    if isinstance(term_data, dict)
                                    else str(term_data)
                                )
                                importance = (
                                    term_data.get("importance", "")
                                    if isinstance(term_data, dict)
                                    else ""
                                )
                                st.caption(f"{term} ({importance})")

                    # Negative signals
                    neg_signals = phase1.get("negative_signals", [])
                    neg_domains = phase1.get("negative_domains", [])
                    if neg_signals or neg_domains:
                        with st.expander("❌ Negative Signals"):
                            st.info(
                                "Negative signals tell the classification system what this patent "
                                "is **NOT** about. They help avoid misclassifications by penalizing "
                                "CPC codes that contain these terms or belong to these domains."
                            )
                            if neg_signals:
                                st.markdown("**Signals:** " + ", ".join(neg_signals))
                            if neg_domains:
                                st.markdown("**Domains:** " + ", ".join(neg_domains))
                            st.caption(
                                "These signals are generated automatically, based in the patents technical content."
                            )

                # Phase 2 ranked candidates
                if phase3:
                    st.markdown("---")
                    st.markdown("### 📊 Phase 2 & 3: Ranked CPC Candidates")
                    for rank, node in enumerate(phase3, 1):
                        symbol = node.get("symbol", "N/A")
                        title = node.get("title", "")
                        score = node.get("score", 0)
                        st.markdown(
                            f"**{rank}. {symbol}** — {title} (score: {score:.2f})"
                        )

                # Phase 4 best code
                if phase4:
                    st.markdown("---")
                    st.markdown("### 🎯 Phase 4: LLM Re-ranking")
                    best = phase4.get("best_code", {})
                    if best:
                        st.metric("Best Code", best.get("symbol", "N/A"))
                        st.metric("Confidence", best.get("confidence", "N/A"))
                        st.markdown(f"**Reasoning:** {best.get('reasoning', 'N/A')}")

                    re_ranked = phase4.get("re_ranked", [])
                    if re_ranked:
                        with st.expander("View Re-ranked List"):
                            for item in re_ranked:
                                st.markdown(
                                    f"{item.get('rank', '')}. {item.get('symbol', '')} — {item.get('justification', '')}"
                                )

                # Full JSON
                with st.expander("📄 View Full Classification JSON"):
                    st.json(cpc_full)

        else:
            st.info("No CPC classification results available.")

# --- TAB 9: STATUS ---
with tab_status:
    st.header("Pipeline Execution Status")

    if not final_state:
        st.info("Run the pipeline to see execution status.")
    else:
        status = final_state.get("status", "UNKNOWN")

        if status == "ERROR":
            st.error(
                f"Pipeline ended with error: {final_state.get('error_message', 'Unknown')}"
            )
        elif status == "WARNING":
            st.warning(
                f"Pipeline ended with warning: {final_state.get('error_message', 'Unknown')}"
            )
        else:
            st.success("Pipeline completed successfully")

        st.markdown("### Step Completion")
        for step, status in st.session_state.pipeline_status.items():
            if status is True:
                st.success(f"✅ {step.replace('_', ' ').title()}")
            elif status is False or status is None:
                st.error(f"❌ {step.replace('_', ' ').title()}")
            else:
                st.warning(f"⚠️ {step.replace('_', ' ').title()}: {status}")

        metadata = final_state.get("metadata", {})
        if metadata:
            st.markdown("### Agent Metadata")
            for agent_name, meta in metadata.items():
                st.caption(f"**{agent_name}:** {meta}")

        warnings = final_state.get("processing_warnings", [])
        if warnings:
            st.markdown("### Processing Warnings")
            for warning in warnings:
                st.warning(warning)

        with st.expander("View Full State (Debug)"):
            st.json(truncate_dict(final_state))
