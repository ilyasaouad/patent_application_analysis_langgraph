from typing import TypedDict, Optional, Dict, Any, List


class GraphState(TypedDict):
    """
    Represents the state of our patent analysis graph.
    """

    # Input file paths (temporarily saved by Streamlit)
    description_path: Optional[str]
    claims_path: Optional[str]
    drawings_path: Optional[str]

    # Extracted text results
    description_text: Optional[str]
    claims_text: Optional[str]
    drawings_text: Optional[str]

    # Metadata
    claims_extracted_from_description: bool

    # AI Detection Results (Agent 2b)
    ai_detection_results: Optional[dict]

    # Claims Clarity Results (Agent 4)
    claims_clarity_results: Optional[dict]

    # Claims Unity Results (Agent 4B)
    claims_unity_results: Optional[dict]

    # Claims Antecedent Results (Agent 4C)
    claims_antecedent_results: Optional[dict]

    # Claims Founded Results (Agent 3B)
    claims_founded_results: Optional[dict]

    # Claims Legal Analysis Results (Agent 4 - Master)
    claims_legal_analysis_results: Optional[dict]

    # CPC Classification Results (Agent 5)
    cpc_classes: Optional[List[str]]
    cpc_classification: Optional[Dict[str, Any]]

    # Status / errors
    status: str
    error_message: Optional[str]
    final_report: Optional[str]
    proposal_letter: Optional[str]

    # Agent reporting
    metadata: Optional[dict]
    processing_warnings: Optional[list]


def create_initial_state(
    description_text: str,
    claims_text: str,
    drawings_text: Optional[str] = None,
) -> GraphState:
    """
    Safely initialize a GraphState dict with all required fields.
    """
    return {
        "description_path": None,
        "claims_path": None,
        "drawings_path": None,
        "description_text": description_text,
        "claims_text": claims_text,
        "drawings_text": drawings_text or "",
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
        "status": "READY",
        "error_message": None,
        "final_report": None,
        "proposal_letter": None,
    }
