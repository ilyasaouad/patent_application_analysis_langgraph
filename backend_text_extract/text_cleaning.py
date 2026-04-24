"""
Shared text-cleaning utilities for patent document processing.

Removes patent page/column label numbers (5, 10, 15, 20, 25, 30, 35)
that appear as artefacts from the original patent PDF layout.
"""
import re
from .encoding_fixer import decode_garbled_pdf_text

# Multiples of 5 that appear as page/column markers in patent PDFs.
# Expanded to 100 as longer patents use higher markers.
LABEL_NUMBERS = {n for n in range(5, 105, 5)}
_LABEL_STRS = {str(n) for n in LABEL_NUMBERS}


def clean_patent_label_numbers(text: str) -> str:
    """
    Remove patent label numbers from text.
    Handles standalone lines and inline markers.
    """
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip().rstrip("\r")

        # Pattern 1: line is ONLY a label number → skip entirely
        if stripped in _LABEL_STRS:
            continue

        # Pattern 2: inline label numbers surrounded by whitespace
        cleaned_line = line
        for num in sorted(LABEL_NUMBERS, reverse=True):  # larger numbers first
            pattern = r"(?<!\d)\s" + str(num) + r"\s(?!\d)"
            cleaned_line = re.sub(pattern, " ", cleaned_line)

        cleaned_lines.append(cleaned_line)

    # Collapse consecutive blank lines
    result_lines: list[str] = []
    prev_blank = False
    for line in cleaned_lines:
        is_blank = line.strip().rstrip("\r") == ""
        if is_blank and prev_blank:
            continue
        result_lines.append(line)
        prev_blank = is_blank

    return "\n".join(result_lines)


def html_tables_to_markdown(text: str) -> str:
    """Converts HTML table tags to basic Markdown tables."""

    def convert_table(match):
        html = match.group(0)
        rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
        if not rows:
            return ""
        md_rows = []
        for i, row in enumerate(rows):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
            cells = [c.strip() for c in cells]
            if not cells:
                continue
            md_rows.append("| " + " | ".join(cells) + " |")
            if i == 0:
                md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
        return "\n".join(md_rows)

    return re.sub(r"<table>.*?</table>", convert_table, text, flags=re.DOTALL)


def full_clean_patent_text(text: str) -> str:
    """
    Unified cleaning pipeline for patent text:
    1. Fix font encoding issues (Caesar +29, etc.)
    2. Convert HTML tables to Markdown
    3. Remove patent label numbers (5-100)
    """
    if not text:
        return ""

    # 1. Fix special PDF encodings
    text = decode_garbled_pdf_text(text)

    # 2. Convert tables
    text = html_tables_to_markdown(text)

    # 3. Clean label numbers
    text = clean_patent_label_numbers(text)

    return text
