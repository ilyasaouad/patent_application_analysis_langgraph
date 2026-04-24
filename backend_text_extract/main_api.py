"""
Main entry point for the Patent Document Analyse Service.
Provides REST API for extracting text from patent documents.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from mineru_wrapper import MinerUWrapper
from config.settings import settings

app = FastAPI(
    title="Patent Document Analyse Service",
    description="Extract text from patent PDFs using MinerU OCR",
    version="1.0.0",
)


class ExtractResponse(BaseModel):
    success: bool
    description_text: Optional[str] = None
    claims_text: Optional[str] = None
    abstract_text: Optional[str] = None
    drawings_text: Optional[str] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Patent Document Analyse Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "mineru_available": MinerUWrapper.is_available()}


@app.post("/extract", response_model=ExtractResponse)
async def extract_document(
    file: UploadFile = File(...), document_type: str = "description"
):
    """
    Extract text from a patent document.

    Args:
        file: PDF, DOCX, or image file
        document_type: "description", "claims", or "drawings"
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: {settings.SUPPORTED_FORMATS}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        wrapper = MinerUWrapper()
        result = wrapper.extract_text(tmp_path, document_type=document_type)

        return ExtractResponse(
            success=True,
            description_text=result.get("description_text"),
            claims_text=result.get("claims_text"),
            abstract_text=result.get("abstract_text"),
            drawings_text=result.get("drawings_text"),
        )
    except Exception as e:
        return ExtractResponse(success=False, error=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/extract/all")
async def extract_all_documents(
    description_file: Optional[UploadFile] = File(None),
    claims_file: Optional[UploadFile] = File(None),
    drawings_file: Optional[UploadFile] = File(None),
):
    """
    Extract text from all patent document types at once.
    """

    async def save_upload(upload_file: UploadFile) -> Optional[str]:
        if not upload_file:
            return None
        ext = Path(upload_file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await upload_file.read())
            return tmp.name

    desc_path = await save_upload(description_file)
    claims_path = await save_upload(claims_file)
    drawings_path = await save_upload(drawings_file)

    try:
        wrapper = MinerUWrapper()
        result = wrapper.extract_all(
            description_path=desc_path,
            claims_path=claims_path,
            drawings_path=drawings_path,
        )

        return JSONResponse(
            content={
                "success": True,
                "description_text": result.get("description_text"),
                "claims_text": result.get("claims_text"),
                "abstract_text": result.get("abstract_text"),
                "drawings_text": result.get("drawings_text"),
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "error": str(e)}, status_code=500
        )
    finally:
        for path in [desc_path, claims_path, drawings_path]:
            if path and os.path.exists(path):
                os.unlink(path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
