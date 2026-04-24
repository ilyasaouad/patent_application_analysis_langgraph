import os
import tempfile
import streamlit as st
from pathlib import Path

from graph_workflow import app_graph
from graph_state import GraphState

st.set_page_config(page_title="LangGraph Patent Analyzer", page_icon="🕸️", layout="wide")

st.title("🕸️ LangGraph Patent Analyzer: Step 1")
st.markdown("Testing the central LangGraph state orchestration for document extraction.")

st.subheader("1. Upload Documents")
col1, col2, col3 = st.columns(3)
with col1:
    desc_file = st.file_uploader("Description PDF", type=["pdf", "docx", "png"])
with col2:
    claims_file = st.file_uploader("Claims PDF", type=["pdf", "docx", "png"])
with col3:
    drawings_file = st.file_uploader("Drawings PDF", type=["pdf", "docx", "png"])

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
        with st.spinner("Saving files temporarily..."):
            desc_path = save_upload(desc_file)
            claims_path = save_upload(claims_file)
            drawings_path = save_upload(drawings_file)
            
        st.info("Files saved. Invoking LangGraph...")
        
        initial_state: GraphState = {
            "description_path": desc_path,
            "claims_path": claims_path,
            "drawings_path": drawings_path,
            "description_text": None,
            "claims_text": None,
            "drawings_text": None,
            "status": "INITIALIZED",
            "error_message": None,
            "final_report": None,
            "proposal_letter": None
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
                
                st.info(f"📝 Agent execution states are being logged securely to `{log_path}`")
                
                step = 1
                for event in app_graph.stream(initial_state):
                    for node_name, state_update in event.items():
                        # Write the Agent Updates to log
                        f.write(f"## ⚙️ Step {step}: Agent `{node_name}` Updates\n```json\n")
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
                st.info("The following letter is a proposed draft for the examiner to send to the applicant.")
                st.markdown(proposal)
                st.markdown("---")
        else:
            st.success("✅ Graph executed successfully!")
            
            st.subheader("Graph Output State")
            
            tab1, tab2, tab3 = st.tabs(["Description Text", "Claims Text", "Drawings Text"])
            
            with tab1:
                txt = final_state.get("description_text")
                if txt:
                    st.text_area("Extracted Description", value=txt, height=400)
                else:
                    st.info("No description text extracted.")
                    
            with tab2:
                txt = final_state.get("claims_text")
                if txt:
                    st.text_area("Extracted Claims", value=txt, height=400)
                else:
                    st.info("No claims text extracted.")
            
            with tab3:
                txt = final_state.get("drawings_text")
                if txt:
                    st.text_area("Extracted Drawings", value=txt, height=400)
                else:
                    st.info("No drawings text extracted.")
