"""
DOCX Extractor - Handles DOCX document text extraction with OCR for images.
"""

from pathlib import Path
from typing import Optional


class DocxExtractor:
    """
    Extracts text from DOCX files, including OCR for embedded images.
    """

    def __init__(self):
        pass

    def extract(self, file_path: str, lang: str = "en") -> str:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file
            lang: Language for OCR

        Returns:
            Extracted text
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX not found: {file_path}")

        return self._extract_with_ocr(path, lang)

    def _extract_with_ocr(self, path: Path, lang: str) -> str:
        """Extract text and OCR images from DOCX."""
        try:
            from backend_text_extract.docx_image_ocr import process_docx_with_ocr

            return process_docx_with_ocr(path, lang=lang)
        except ImportError:
            return self._extract_text_only(path)

    def _extract_text_only(self, path: Path) -> str:
        """Extract text without OCR (fallback)."""
        try:
            from docx import Document
            from backend_text_extract.docx_image_ocr import _get_para_number_text

            doc = Document(path)
            text_parts = []
            for para in doc.paragraphs:
                para_text = para.text
                num_prefix = _get_para_number_text(para)
                if num_prefix:
                    para_text = f"{num_prefix} {para_text}"
                if para_text.strip():
                    text_parts.append(para_text)
            return "\n".join(text_parts)
        except ImportError:
            raise ImportError("python-docx not installed")
