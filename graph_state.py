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
    
    # Status / errors
    status: str
    error_message: Optional[str]
    final_report: Optional[str]
    proposal_letter: Optional[str]
