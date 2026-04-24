"""
MinerU Wrapper - Provides interface for MinerU document extraction.

Uses a 3-layer approach for drawings (ported from drawing_reader_subagent):
  1. PyMuPDF (fitz) for structural text extraction directly from PDF
  2. MinerU for layout-aware OCR extraction
  3. Tesseract for deep OCR on cropped images
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MINERU_AVAILABLE = True


class MinerUWrapper:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or tempfile.gettempdir()

    def _convert_docx_to_pdf(self, docx_path: Path) -> Path:
        """Convert a DOCX file to PDF so MinerU can process it."""
        import docx2pdf

        pdf_path = Path(tempfile.mktemp(suffix=".pdf", dir=self.output_dir))
        docx2pdf.convert(str(docx_path), str(pdf_path))
        return pdf_path

    def _ensure_pdf(self, path: Path) -> Tuple[Path, bool]:
        """If the file is a DOCX, convert it to PDF. Returns (pdf_path, was_converted)."""
        if path.suffix.lower() == ".docx":
            pdf_path = self._convert_docx_to_pdf(path)
            return pdf_path, True
        return path, False

    def extract(
        self, file_path: str, method: str = "auto", lang: str = "en"
    ) -> Tuple[str, str]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() == ".docx":
            try:
                # Attempt to convert DOCX to PDF so MinerU can perform advanced layout OCR
                pdf_path, was_converted = self._ensure_pdf(path)
                try:
                    return self._extract_with_mineru(pdf_path, method, lang)
                finally:
                    if was_converted and pdf_path.exists():
                        pdf_path.unlink()
            except Exception as e:
                # Microsoft Word COM Error (e.g., Open.SaveAs) occurred.
                # Fallback to the native DocxExtractor that bypasses PDF conversion entirely!
                print(
                    f"MinerU docx2pdf conversion failed ({str(e)}). Automatically falling back to native Python DocxExtractor."
                )
                from backend_text_extract.docx_extractor import DocxExtractor

                extractor = DocxExtractor()
                text = extractor.extract(str(path), lang=lang)
                return text, str(path)
        else:
            return self._extract_with_mineru(path, method, lang)

    def _extract_with_mineru(
        self, path: Path, method: str, lang: str
    ) -> Tuple[str, str]:
        """Standard extraction: MinerU + image OCR replacement."""
        from mineru.cli.common import do_parse, read_fn
        from backend_text_extract.image_ocr import ImageOCR

        run_output = tempfile.mkdtemp(prefix="mineru_extract_", dir=self.output_dir)
        pdf_bytes = read_fn(path)
        file_name = Path(path).stem
        do_parse(
            output_dir=run_output,
            pdf_file_names=[file_name],
            pdf_bytes_list=[pdf_bytes],
            p_lang_list=[lang],
            backend="pipeline",
            parse_method=method,
        )

        ocr = ImageOCR(lang=lang)

        for root, _, files in os.walk(run_output):
            for f in files:
                if f.endswith(".md") and not f.endswith("_layout.md"):
                    res_path = os.path.join(root, f)
                    with open(res_path, "r", encoding="utf-8") as fh:
                        md_content = fh.read()

                    def replace_image(match):
                        img_rel_path = match.group(1)
                        img_full_path = os.path.join(root, img_rel_path)
                        if os.path.exists(img_full_path):
                            try:
                                text = ocr.extract_text(img_full_path)
                                return (
                                    f"[Image OCR Content]:\n{text}"
                                    if text.strip()
                                    else ""
                                )
                            except Exception as e:
                                return f"[Image OCR Failed: {e}]"
                        return match.group(0)

                    md_content = re.sub(r"!\[.*?\]\((.*?)\)", replace_image, md_content)
                    return md_content, res_path
        raise RuntimeError("No Markdown output generated")

    def _extract_drawings(self, path: Path, method: str, lang: str) -> Tuple[str, str]:
        """
        3-layer extraction specifically for patent drawings.
        Ported from drawing_reader_subagent for best quality.

        Layer 1: PyMuPDF structural text (direct text from PDF, no OCR needed)
        Layer 2: MinerU layout-aware extraction (understands page structure)
        Layer 3: Tesseract deep OCR on cropped images (catches scattered labels)
        """
        from mineru.cli.common import do_parse, read_fn
        from backend_text_extract.text_cleaning import full_clean_patent_text

        extracted_parts = []

        # ── Layer 1: PyMuPDF structural text ──
        try:
            import fitz

            doc = fitz.open(str(path))
            text_blocks = []
            for page_num, page in enumerate(doc):
                page_text = page.get_text().strip()
                if page_text:
                    text_blocks.append(f"--- Page {page_num + 1} ---\n{page_text}")
            if text_blocks:
                extracted_parts.append("\n".join(text_blocks))
            doc.close()
        except ImportError:
            pass
        except Exception as e:
            print(f"[MinerUWrapper] PyMuPDF pass failed: {e}")

        # ── Layer 2: MinerU layout-aware extraction ──
        run_output = tempfile.mkdtemp(prefix="draw_extract_", dir=self.output_dir)
        try:
            pdf_bytes = read_fn(path)
            file_name = Path(path).stem
            do_parse(
                output_dir=run_output,
                pdf_file_names=[file_name],
                pdf_bytes_list=[pdf_bytes],
                p_lang_list=[lang],
                backend="pipeline",
                parse_method="ocr",
                formula_enable=False,
                table_enable=False,
            )

            md_text = ""
            for root, _, files in os.walk(run_output):
                for f in files:
                    if f.endswith(".md") and not f.endswith("_layout.md"):
                        with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                            content = fh.read()
                            # Remove markdown image links
                            content = re.sub(r"!\[.*?\]\(images/.*?\)", "", content)
                            # Remove redundant "Figure X" captions
                            content = re.sub(
                                r"(?i)^\s*figure\s+\d+[a-z]?\s*$",
                                "",
                                content,
                                flags=re.MULTILINE,
                            )
                            md_text += content

            if md_text.strip():
                md_text = re.sub(r"\n{3,}", "\n\n", md_text).strip()
                extracted_parts.append(md_text)

            # ── Layer 3: Surya deep OCR on cropped images ──
            try:
                from PIL import Image
                from backend_text_extract.image_ocr import ImageOCR

                ocr = ImageOCR(lang=lang)

                # Find all images in the MinerU output
                img_files = []
                for root, _, files in os.walk(run_output):
                    for f in files:
                        if f.lower().endswith((".jpg", ".jpeg", ".png")):
                            img_files.append(Path(root) / f)

                if img_files:
                    temp_ocr_results = []
                    for img_file in img_files:
                        try:
                            img_text = ocr.extract_text(str(img_file))
                            if img_text.strip():
                                temp_ocr_results.append(
                                    f"\n[Text from {img_file.name}]:\n{img_text.strip()}"
                                )
                        except Exception:
                            pass

                    if temp_ocr_results:
                        extracted_parts.extend(temp_ocr_results)
            except ImportError:
                pass

        except Exception as e:
            extracted_parts.append(f"\n[MinerU Error]: {str(e)}")

        # ── Combine and clean ──
        final_text = "\n\n".join(extracted_parts)

        # Apply the drawing-specific cleanup (remove garbled strings, duplicates)
        lines = final_text.split("\n")
        seen_content = set()
        kept_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("=") or line.startswith("-") or line.startswith("["):
                continue
            keep = False
            if re.search(r"\d", line):
                keep = True
            elif len(line) < 60:
                keep = True
            if keep:
                norm_line = re.sub(r"\s+", " ", line.lower())
                if norm_line not in seen_content:
                    seen_content.add(norm_line)
                    kept_lines.append(line)

        cleaned_text = "\n".join(kept_lines)
        cleaned_text = full_clean_patent_text(cleaned_text)

        return cleaned_text, None

    def extract_all(
        self,
        description_path: Optional[str] = None,
        claims_path: Optional[str] = None,
        drawings_path: Optional[str] = None,
        method: str = "auto",
        lang: str = "en",
    ) -> Dict[str, str]:
        result = {}

        if description_path:
            desc_text, _ = self.extract(description_path, method, lang)
            result["description_text"] = desc_text
        else:
            result["description_text"] = ""

        if claims_path:
            claims_text, _ = self.extract(claims_path, method, lang)
            result["claims_text"] = claims_text
        else:
            result["claims_text"] = ""

        if drawings_path:
            draw_path = Path(drawings_path)
            if draw_path.suffix.lower() == ".docx":
                try:
                    # Auto-convert DOCX to PDF if needed, then use 3-layer drawing extraction
                    pdf_path, was_converted = self._ensure_pdf(draw_path)
                    try:
                        drawings_text, _ = self._extract_drawings(
                            pdf_path, method, lang
                        )
                    finally:
                        if was_converted and pdf_path.exists():
                            pdf_path.unlink()
                except Exception as e:
                    print(
                        f"Drawings docx2pdf conversion failed ({str(e)}). Falling back to DocxExtractor."
                    )
                    from backend_text_extract.docx_extractor import DocxExtractor

                    extractor = DocxExtractor()
                    drawings_text = extractor.extract(str(draw_path), lang=lang)
            else:
                drawings_text, _ = self._extract_drawings(draw_path, method, lang)

            result["drawings_text"] = drawings_text
        else:
            result["drawings_text"] = ""
        return result

    def extract_multiple(
        self, file_paths: List[str], method: str = "auto", lang: str = "en"
    ) -> List[Tuple[str, str]]:
        results = []
        for file_path in file_paths:
            try:
                result = self.extract(file_path, method, lang)
                results.append(result)
            except Exception as e:
                results.append((f"Error: {str(e)}", None))
        return results
