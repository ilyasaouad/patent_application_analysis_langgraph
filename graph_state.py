from typing import TypedDict, Optional


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

    # Status / errors
    status: str
    error_message: Optional[str]
    final_report: Optional[str]
    proposal_letter: Optional[str]
