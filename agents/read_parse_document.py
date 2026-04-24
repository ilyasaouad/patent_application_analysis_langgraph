from graph_state import GraphState
from backend_text_extract.mineru_wrapper import MinerUWrapper


def read_parse_document(state: GraphState) -> GraphState:
    """
    LangGraph Node: Reads PDF documents from temporary paths using MinerU backend,
    and returns a state update containing the extracted texts.
    """
    desc_path = state.get("description_path")
    claims_path = state.get("claims_path")
    draw_path = state.get("drawings_path")

    print(
        f"[Extractor Node] Received files: Desc={desc_path}, Claims={claims_path}, Draw={draw_path}"
    )

    # Handle case where no files provided
    if not desc_path and not claims_path and not draw_path:
        return {
            "description_text": "",
            "claims_text": "",
            "drawings_text": "",
            "status": "SUCCESS",
            "error_message": None,
        }

    try:
        wrapper = MinerUWrapper()
        result = wrapper.extract_all(
            description_path=desc_path, claims_path=claims_path, drawings_path=draw_path
        )

        return {
            "description_text": result.get("description_text") or "",
            "claims_text": result.get("claims_text") or "",
            "drawings_text": result.get("drawings_text") or "",
            "status": "SUCCESS",
            "error_message": None,
        }
    except Exception as e:
        print(f"[Extractor Node] ERROR: {e}")
        return {"status": "ERROR", "error_message": str(e)}
