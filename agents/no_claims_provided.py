import os
from graph_state import GraphState

# Resources path for this agent
AGENT_RESOURCES = os.path.join("resources_for_agents", "no_claims_provided")


def no_claims_provided(state: GraphState) -> GraphState:
    """
    LangGraph Node: Triggered when no claims could be identified anywhere.
    Halts execution by formatting a formal rejection report based on NIPO guidelines.
    """
    print("[No Claims Provided Node] TRIGGERED. Halting due to missing patent claims.")

    # Load guidelines
    guideline_path = os.path.join(AGENT_RESOURCES, "guidelines.md")
    report_text = ""
    if os.path.exists(guideline_path):
        with open(guideline_path, "r", encoding="utf-8") as f:
            report_text = f.read()
    else:
        report_text = "# Formal Rejection\nError: Could not locate guidelines."

    # Load rejection letter template
    letter_path = os.path.join(AGENT_RESOURCES, "rejection_letter.md")
    proposal_text = ""
    if os.path.exists(letter_path):
        with open(letter_path, "r", encoding="utf-8") as f:
            proposal_text = f.read()
    else:
        proposal_text = "Error: Could not locate rejection letter template."

    return {
        "status": "ERROR",
        "error_message": "Analysis halted: No patent claims sequence could be provided or extracted from the documents.",
        "final_report": report_text,
        "proposal_letter": proposal_text,
    }
