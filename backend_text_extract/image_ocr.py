"""
Image OCR - Handles OCR extraction from images using Surya OCR.

Surya is a pure-Python OCR engine (no .exe needed) that provides
much better accuracy than Tesseract, especially for patent drawings
with scattered labels and reference numerals.
"""

from pathlib import Path
from typing import Optional


# Lazy-loaded Surya predictors (shared across calls to avoid reloading models)
_foundation_predictor = None
_recognition_predictor = None
_detection_predictor = None


def _get_surya_predictors():
    """Initialize Surya predictors once and reuse them."""
    global _foundation_predictor, _recognition_predictor, _detection_predictor

    if _foundation_predictor is None:
        from surya.foundation import FoundationPredictor
        from surya.recognition import RecognitionPredictor
        from surya.detection import DetectionPredictor

        _foundation_predictor = FoundationPredictor()
        _recognition_predictor = RecognitionPredictor(_foundation_predictor)
        _detection_predictor = DetectionPredictor()

    return _recognition_predictor, _detection_predictor


class ImageOCR:
    """
    Performs OCR on image files (PNG, JPG, TIFF, BMP) using Surya OCR.
    """

    def __init__(self, lang: str = "en"):
        self.lang = lang

    def extract_text(self, file_path: str, lang: Optional[str] = None) -> str:
        """
        Extract text from image using Surya OCR.

        Args:
            file_path: Path to image file
            lang: Language code (not used by Surya, kept for API compatibility)

        Returns:
            Extracted text
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        return self._ocr_image(path)

    def _ocr_image(self, path: Path) -> str:
        """Perform OCR on image using Surya."""
        from PIL import Image

        recognition_predictor, detection_predictor = _get_surya_predictors()

        image = Image.open(path)
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        predictions = recognition_predictor([image], det_predictor=detection_predictor)

        # Extract text from all detected lines
        lines = []
        if predictions and len(predictions) > 0:
            for text_line in predictions[0].text_lines:
                text = text_line.text.strip()
                if text:
                    lines.append(text)

        # Apply drawing-specific cleaning
        from .text_cleaning import full_clean_patent_text
        import re

        kept_lines = []
        seen_content = set()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            keep = False
            # Keep if has digit (good for reference numerals) or looks like a short label
            if re.search(r'\d', line) or len(line) < 60:
                keep = True

            if keep:
                norm_line = re.sub(r'\s+', ' ', line.lower())
                if norm_line not in seen_content:
                    seen_content.add(norm_line)
                    kept_lines.append(line)

        cleaned_text = '\n'.join(kept_lines)
        return full_clean_patent_text(cleaned_text)

    def extract_with_layout(self, file_path: str) -> dict:
        """
        Extract text with layout information (bounding boxes).

        Returns:
            Dict with text lines and their bounding boxes
        """
        from PIL import Image

        recognition_predictor, detection_predictor = _get_surya_predictors()

        image = Image.open(file_path)
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        predictions = recognition_predictor([image], det_predictor=detection_predictor)

        result = {"text_lines": [], "bboxes": [], "confidences": []}
        if predictions and len(predictions) > 0:
            for text_line in predictions[0].text_lines:
                result["text_lines"].append(text_line.text)
                result["bboxes"].append(text_line.bbox)
                result["confidences"].append(text_line.confidence)

        return result
