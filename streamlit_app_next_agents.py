"""
streamlit_app_next_agents.py
============================
Continuation app - reads extracted documents and runs Agent 4 (Claims Clarity).
No extraction, no upload - reads directly from output_text_documents/

Prerequisites:
    - output_text_documents/description.md
    - output_text_documents/claims.md
    - output_text_documents/drawings.md (optional)
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import streamlit as st

from agents.agent4_claims_clarity.claims_clarity_agent import claims_clarity_agent
from agents.agent4b_claims_unity.claims_unity_agent import claims_unity_agent
from agents.agent4c_claims_antecedent.claims_antecedent_agent import (
    claims_antecedent_agent,
)

# Page config
st.set_page_config(
    page_title="Patent Analysis - Next Agents", page_icon="🔍", layout="wide"
)

# Directories
INPUT_DIR = Path("output_text_documents")
CLARITY_DIR = Path("claims_analyse_reports/clarity_analyse")
UNITY_DIR = Path("claims_analyse_reports/unity_analyse")
CLARITY_DIR.mkdir(exist_ok=True)
UNITY_DIR.mkdir(exist_ok=True)

# Cache files for tracking last run
CACHE_FILE = CLARITY_DIR / ".last_run_cache"
UNITY_CACHE_FILE = UNITY_DIR / ".unity_last_run"


def get_file_modification_time(filepath: Path) -> float:
    """Get the last modification time of a file."""
    if filepath.exists():
        return filepath.stat().st_mtime
    return 0


def check_files_changed() -> bool:
    """Check if input files have changed since last run."""
    if not CACHE_FILE.exists():
        return True

    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    except:
        return True

    current_times = {}
    for filename in ["description.md", "claims.md", "drawings.md"]:
        filepath = INPUT_DIR / filename
        current_times[filename] = get_file_modification_time(filepath)

    # Check if any file has changed
    for filename, current_time in current_times.items():
        cached_time = cache.get(filename, 0)
        if current_time != cached_time:
            return True

    return False


def update_cache():
    """Update the cache with current file modification times."""
    cache = {}
    for filename in ["description.md", "claims.md", "drawings.md"]:
        filepath = INPUT_DIR / filename
        cache[filename] = get_file_modification_time(filepath)

    cache["last_run_timestamp"] = time.time()

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


# ============================================================================
# MAIN APP
# ============================================================================

st.title("🔍 Patent Analysis - Next Agents")
st.markdown("**Continuation of patent analysis pipeline**")
st.markdown("Reads extracted documents from `output_text_documents/`")
st.markdown("---")

# Check prerequisites
st.subheader("📋 Document Status")

prereq_col1, prereq_col2, prereq_col3 = st.columns(3)

has_desc = (INPUT_DIR / "description.md").exists()
has_claims = (INPUT_DIR / "claims.md").exists()
has_drawings = (INPUT_DIR / "drawings.md").exists()

with prereq_col1:
    st.metric("Description", "✅ Found" if has_desc else "❌ Missing")
with prereq_col2:
    st.metric("Claims", "✅ Found" if has_claims else "❌ Missing")
with prereq_col3:
    st.metric("Drawings", "✅ Found" if has_drawings else "⚪ Optional")

if not has_desc or not has_claims:
    st.error(
        """
    ❌ **Required files missing!**
    
    Please run the extraction pipeline first to generate:
    - `output_text_documents/description.md`
    - `output_text_documents/claims.md`
    
    Run: `streamlit run streamlit_app.py`
    """
    )
    st.stop()

# Load documents
with open(INPUT_DIR / "description.md", "r", encoding="utf-8") as f:
    description_text = f.read()

with open(INPUT_DIR / "claims.md", "r", encoding="utf-8") as f:
    claims_text = f.read()

drawings_text = ""
if has_drawings:
    with open(INPUT_DIR / "drawings.md", "r", encoding="utf-8") as f:
        drawings_text = f.read()

# Show file stats
st.markdown("---")
st.subheader("📄 Document Information")

stats_col1, stats_col2, stats_col3 = st.columns(3)
with stats_col1:
    st.metric("Description", f"{len(description_text):,} chars")
with stats_col2:
    st.metric("Claims", f"{len(claims_text):,} chars")
with stats_col3:
    st.metric("Drawings", f"{len(drawings_text):,} chars" if has_drawings else "N/A")

# ============================================================================
# TABS
# ============================================================================

st.markdown("---")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📑 Description",
        "⚖️ Claims",
        "🖼️ Drawings",
        "🔍 Claims Clarity",
        "🔗 Claims Unity",
        "📎 Antecedent Basis",
    ]
)

with tab1:
    st.text_area(
        "Description Content",
        value=description_text,
        height=600,
        disabled=True,
        key="desc_view",
    )

with tab2:
    st.text_area(
        "Claims Content",
        value=claims_text,
        height=600,
        disabled=True,
        key="claims_view",
    )

with tab3:
    if has_drawings:
        st.text_area(
            "Drawings Content",
            value=drawings_text,
            height=600,
            disabled=True,
            key="drawings_view",
        )
    else:
        st.info("No drawings file found in output_text_documents/")

with tab4:
    st.subheader("NIPO § 8 Legal Analysis")
    st.caption("Analyzes Enablement, Clarity, and Support")

    # Check cache status
    files_changed = check_files_changed()

    if files_changed:
        st.info(
            "📝 Input files have changed or no previous analysis found. Will run new analysis."
        )

    # Always show re-run button
    force_rerun = st.button("🔄 Force Re-run Analysis", type="secondary")

    # Determine if we should run
    should_run = files_changed or force_rerun

    # Check if we have cached results
    cached_result = None
    if not should_run and (CLARITY_DIR / "claims_clarity_result.json").exists():
        try:
            with open(
                CLARITY_DIR / "claims_clarity_result.json", "r", encoding="utf-8"
            ) as f:
                cached_data = json.load(f)
                if cached_data.get("status") == "SUCCESS":
                    cached_result = cached_data
                    st.success("✅ Showing cached results (files unchanged)")
        except:
            pass

    # Run analysis if needed
    clarity_result = cached_result

    if should_run or not clarity_result:
        with st.spinner(
            "Running NIPO § 8 Claims Clarity Analysis... This may take several minutes."
        ):
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

            try:
                result_update = claims_clarity_agent(state)
                if result_update:
                    clarity_result = result_update.get("claims_clarity_results")
                    # Update cache
                    update_cache()
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                import traceback

                st.code(traceback.format_exc())
                clarity_result = None

    # Display results
    if clarity_result and clarity_result.get("status") == "SUCCESS":
        # Overall assessment
        overall = clarity_result.get("overall", {})

        st.markdown("---")
        st.subheader("📊 Overall Assessment")

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            decision = overall.get("examination_decision", "N/A")
            decision_icon = (
                "🟢"
                if decision == "GRANT"
                else "🟡"
                if decision == "FURTHER_EXAMINATION"
                else "🔴"
            )
            st.metric("Decision", f"{decision_icon} {decision}")
        with metric_col2:
            st.metric("Risk Level", overall.get("risk_level", "N/A"))
        with metric_col3:
            st.metric("Critical Issues", len(overall.get("critical_issues", [])))

        # Summary
        st.markdown("### 📝 Summary")
        st.info(overall.get("summary", "No summary available."))

        # Detailed analysis tabs
        st.markdown("---")
        st.subheader("Detailed Analysis")

        detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(
            ["📐 Enablement", "🔍 Clarity", "📝 Support", "📄 Formal Report"]
        )

        with detail_tab1:
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

        with detail_tab2:
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

        with detail_tab3:
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

        with detail_tab4:
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

        # Output files info
        st.markdown("---")
        st.subheader("📁 Output Files")
        st.markdown(f"**Saved to:** `{CLARITY_DIR}`")

        if CLARITY_DIR.exists():
            files = [f.name for f in CLARITY_DIR.iterdir() if f.is_file()]
            if files:
                st.code("\n".join(files))

        # Raw JSON (expandable)
        st.markdown("---")
        with st.expander("🔧 Raw JSON Output (Debug)"):
            st.json(clarity_result)

    elif clarity_result and clarity_result.get("status") == "ERROR":
        st.error(f"❌ Analysis Error: {clarity_result.get('error', 'Unknown')}")
        if clarity_result.get("message"):
            st.info(clarity_result["message"])
    else:
        st.warning("No analysis results available.")

# ============================================================================
# TAB 5: CLAIMS UNITY ANALYSIS (Agent 4B)
# ============================================================================

with tab5:
    st.subheader("🔗 Claims Unity Analysis")
    st.caption("Agent 4B — Norwegian Patents Act §10 / Patent Regulations §8")
    st.markdown(
        "Analyzes whether claims constitute a single invention or multiple mutually independent inventions."
    )

    # Auto-run unity analysis
    unity_result = None

    # Check cache
    unity_cache_file = UNITY_DIR / ".unity_last_run"
    should_run_unity = True

    if unity_cache_file.exists():
        try:
            with open(unity_cache_file, "r") as f:
                unity_cache = json.load(f)
            # Check if claims file changed
            claims_mtime = (INPUT_DIR / "claims.md").stat().st_mtime
            if unity_cache.get("claims_mtime") == claims_mtime:
                should_run_unity = False
                # Load cached result
                unity_json_path = UNITY_DIR / "claims_unity_result.json"
                if unity_json_path.exists():
                    with open(unity_json_path, "r", encoding="utf-8") as f:
                        unity_result = json.load(f)
                    st.success("✅ Showing cached unity results (claims unchanged)")
        except:
            should_run_unity = True

    force_rerun_unity = st.button("🔄 Force Re-run Unity Analysis", type="secondary")

    if should_run_unity or force_rerun_unity:
        with st.spinner(
            "Running Claims Unity Analysis... This may take several minutes."
        ):
            try:
                unity_state_update = claims_unity_agent(
                    {
                        "claims_text": claims_text,
                        "description_text": description_text,
                        "drawings_text": drawings_text,
                    }
                )
                if unity_state_update:
                    unity_result = unity_state_update.get("claims_unity_results")
                    # Update cache
                    claims_mtime = (INPUT_DIR / "claims.md").stat().st_mtime
                    with open(unity_cache_file, "w") as f:
                        json.dump({"claims_mtime": claims_mtime}, f)
            except Exception as e:
                st.error(f"Unity analysis failed: {e}")
                import traceback

                st.code(traceback.format_exc())
                unity_result = None

    if unity_result and unity_result.get("status") == "SUCCESS":
        # Overall metrics
        conclusion = unity_result.get("conclusion", "N/A")

        col1, col2, col3 = st.columns(3)
        with col1:
            icon = "🟢" if conclusion == "SINGLE_INVENTION" else "🔴"
            st.metric("Conclusion", f"{icon} {conclusion}")
        with col2:
            st.metric("Confidence", unity_result.get("confidence", "N/A"))
        with col3:
            groups_count = len(unity_result.get("grouping", []))
            st.metric("Groups Found", groups_count)

        # Status reason
        st.markdown("### 📝 Status Reason")
        st.info(unity_result.get("status_reason", ""))

        # Grouping details
        grouping = unity_result.get("grouping", [])
        if grouping:
            st.markdown("---")
            st.subheader("📊 Claim Grouping")

            for group in grouping:
                with st.expander(
                    f"Group {group.get('group_no', 'N/A')}: {group.get('technical_subject_matter', '')}"
                ):
                    st.markdown(
                        f"**Representative Claims:** {', '.join(group.get('representative_independent_claims', []))}"
                    )

                    dep_claims = group.get("included_dependent_claims", [])
                    if dep_claims:
                        st.markdown(f"**Dependent Claims:** {', '.join(dep_claims)}")

                    st.markdown(
                        f"**Technical Problem:** {group.get('objective_technical_problem', '')}"
                    )

                    special_features = group.get("special_technical_features", [])
                    if special_features:
                        st.markdown("**Special Technical Features:**")
                        for feat in special_features:
                            st.markdown(f"- {feat}")

                    links = group.get("links_to_description", [])
                    if links:
                        st.markdown(f"**Links to Description:** {', '.join(links)}")

        # Common features
        common = unity_result.get("common_features", [])
        if common:
            st.markdown("---")
            st.markdown("### 🔗 Common Features")
            for feat in common:
                st.markdown(f"- {feat}")

        # Technical relationship analysis
        analysis = unity_result.get("technical_relationship_analysis", "")
        if analysis:
            st.markdown("---")
            st.markdown("### 🔍 Technical Relationship Analysis")
            st.write(analysis)

        # Legal mapping
        legal = unity_result.get("legal_mapping", "")
        if legal:
            st.markdown("---")
            st.markdown("### ⚖️ Legal Mapping")
            st.write(legal)

        # Recommendation
        rec = unity_result.get("recommendation", "")
        if rec:
            st.markdown("---")
            st.markdown("### 🎯 Recommendation")
            st.success(rec)

        # Rejection Letter (if multiple inventions)
        if unity_result.get("conclusion") == "MULTIPLE_INVENTIONS":
            st.markdown("---")
            st.subheader("📄 NIPO Rejection Letter")
            st.warning(
                "⚠️ The application does not comply with Norwegian Patents Act, Section 10"
            )

            rejection_letter = unity_result.get("rejection_letter", "")
            if rejection_letter:
                st.markdown(rejection_letter)
            else:
                st.info(
                    "No rejection letter was generated. Check the raw JSON for details."
                )

            # Save to file if not already saved
            rejection_path = UNITY_DIR / "claims_unity_rejection_letter.md"
            if not rejection_path.exists() and rejection_letter:
                with open(rejection_path, "w", encoding="utf-8") as f:
                    f.write("# NIPO Unity Rejection Letter\n\n")
                    f.write("## Norwegian Patents Act §10 / Patent Regulations §8\n\n")
                    f.write(rejection_letter)
                st.caption(f"Saved to: {rejection_path}")

        # Exemplar analogies
        exemplars = unity_result.get("exemplar_analogies_used", [])
        if exemplars:
            st.markdown("---")
            st.subheader("📚 Exemplar Analogies")
            for ex in exemplars:
                with st.expander(f"{ex.get('case_id', 'N/A')}"):
                    st.markdown(f"**Summary:** {ex.get('one_line_summary', '')}")
                    st.markdown(f"**Mapping:** {ex.get('mapping', '')}")
                    excerpt = ex.get("quoted_excerpt", "")
                    if excerpt and excerpt != "no exemplar excerpt available":
                        st.markdown("**Excerpt:**")
                        st.code(excerpt)

        # Output files
        st.markdown("---")
        st.subheader("📁 Output Files")
        unity_files = [
            f.name
            for f in UNITY_DIR.iterdir()
            if f.is_file() and "unity" in f.name.lower()
        ]
        if unity_files:
            st.code("\n".join(unity_files))

        # Raw JSON
        st.markdown("---")
        with st.expander("🔧 Raw JSON Output (Debug)"):
            st.json(unity_result)

    elif unity_result and unity_result.get("status") == "ERROR":
        st.error(f"❌ Unity Analysis Error: {unity_result.get('error', 'Unknown')}")
        if unity_result.get("message"):
            st.info(unity_result["message"])
    else:
        st.warning("No unity analysis results available.")

st.markdown("---")
st.caption(
    "Patent Analysis Pipeline — Agent 4: Claims Clarity (NIPO § 8) | Agent 4B: Claims Unity (NIPO § 10)"
)
