import subprocess
import sys

# Auto-install missing dependencies that MinerU requires
try:
    import albumentations
except ImportError:
    print("[Extractor Node] Installing missing dependency: albumentations...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "albumentations", "-q"]
    )
    import albumentations

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

        # Use extract_all like the working project does
        result = wrapper.extract_all(
            description_path=desc_path,
            claims_path=claims_path,
            drawings_path=draw_path,
        )

        desc_text = result.get("description_text", "") or ""
        claims_text = result.get("claims_text", "") or ""
        drawings_text = result.get("drawings_text", "") or ""

        print(f"[Extractor Node] Extraction complete:")
        print(f"  - Description: {len(desc_text)} chars")
        print(f"  - Claims: {len(claims_text)} chars")
        print(f"  - Drawings: {len(drawings_text)} chars")

        # Check if texts are empty when files were provided
        warnings = []
        if desc_path and not desc_text.strip():
            warnings.append("Description file provided but extracted text is empty")
        if claims_path and not claims_text.strip():
            warnings.append("Claims file provided but extracted text is empty")
        if draw_path and not drawings_text.strip():
            warnings.append("Drawings file provided but extracted text is empty")

        if warnings:
            warning_msg = "; ".join(warnings)
            print(f"[Extractor Node] Warnings: {warning_msg}")
            return {
                "description_text": desc_text,
                "claims_text": claims_text,
                "drawings_text": drawings_text,
                "status": "WARNING",
                "error_message": warning_msg,
            }

        return {
            "description_text": desc_text,
            "claims_text": claims_text,
            "drawings_text": drawings_text,
            "status": "SUCCESS",
            "error_message": None,
        }
    except Exception as e:
        print(f"[Extractor Node] CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {
            "description_text": "",
            "claims_text": "",
            "drawings_text": "",
            "status": "ERROR",
            "error_message": str(e),
        }
