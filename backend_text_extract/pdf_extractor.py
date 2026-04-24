"""
PDF Extractor - Handles PDF document text extraction.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class PDFExtractor:
    """
    Handles PDF text extraction using MinerU.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or tempfile.gettempdir()

    def extract(
        self, file_path: str, method: str = "auto", lang: str = "en"
    ) -> Tuple[str, str]:
        """
        Extract text from PDF.

        Args:
            file_path: Path to PDF file
            method: Extraction method ("auto", "ocr", "ocr_only")
            lang: Language code

        Returns:
            Tuple of (extracted_text, output_file_path)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        return self._extract_with_mineru(path, method, lang)

    def _extract_with_mineru(
        self, path: Path, method: str, lang: str
    ) -> Tuple[str, str]:
        """Use MinerU to extract text from PDF."""
        from backend_text_extract.mineru_wrapper import MINERU_AVAILABLE

        if not MINERU_AVAILABLE:
            return "MinerU not available", None

        from backend_text_extract.demo.demo import parse_doc

        run_output = tempfile.mkdtemp(prefix="pdf_extract_", dir=self.output_dir)

        parse_doc(
            path_list=[path],
            output_dir=run_output,
            lang=lang,
            backend="pipeline",
            method=method,
            formula_enable=False,
            table_enable=True,
        )

        for root, _, files in os.walk(run_output):
            for f in files:
                if f.endswith(".md") and not f.endswith("_layout.md"):
                    res_path = os.path.join(root, f)
                    with open(res_path, "r", encoding="utf-8") as fh:
                        return fh.read(), res_path

        raise RuntimeError("No Markdown output generated")

    def extract_pages(self, file_path: str, pages: list, lang: str = "en") -> str:
        """
        Extract text from specific pages.

        Args:
            file_path: Path to PDF
            pages: List of page numbers (1-indexed)
            lang: Language code

        Returns:
            Combined text from specified pages
        """
        raise NotImplementedError("Page-specific extraction not yet implemented")
