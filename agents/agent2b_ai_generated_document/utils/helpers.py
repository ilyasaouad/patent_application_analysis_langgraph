"""
utils/helpers.py
================
Utility functions for text processing and JSON extraction
"""

import json
import re
from typing import Dict, Any


def truncate_text(text: str, max_chars: int) -> str:
    """
    Safely truncate text while preserving readability.
    Tries to cut at sentence boundary if possible.
    
    Args:
        text: Text to truncate
        max_chars: Maximum number of characters
    
    Returns:
        str: Truncated text
    """
    if len(text) <= max_chars:
        return text
    
    # Try to cut at sentence boundary
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    
    # Only use period boundary if it's not too far back
    if last_period > max_chars * 0.8:
        return truncated[:last_period + 1]
    
    return truncated + "..."


def parse_json_safe(response: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Robustly extract JSON from LLM response.
    Handles multiple formats and edge cases.
    
    Args:
        response: LLM response text (may contain JSON)
        fallback: Fallback dictionary if parsing fails
    
    Returns:
        dict: Parsed JSON or fallback
    """
    # Method 1: Direct JSON extraction
    try:
        if "{" in response and "}" in response:
            json_start = response.index("{")
            json_end = response.rindex("}") + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except Exception as e:
        pass
    
    # Method 2: Regex extraction (find all JSON-like blocks)
    try:
        candidates = re.findall(r"\{[\s\S]*?\}", response)
        
        # Try parsing candidates in reverse order (last is often best)
        for chunk in reversed(candidates):
            try:
                return json.loads(chunk)
            except Exception:
                continue
    except Exception:
        pass
    
    # Method 3: Strip markdown code blocks
    try:
        if "```json" in response.lower():
            # Extract from code block
            parts = re.split(r"```json|```", response, flags=re.IGNORECASE)
            for part in parts:
                part = part.strip()
                if part and part.startswith("{"):
                    return json.loads(part)
    except Exception:
        pass
    
    return fallback


def validate_json_structure(data: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that JSON contains required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
    
    Returns:
        bool: True if all required keys present
    """
    return all(key in data for key in required_keys)


def normalize_score(score: Any, default: float = 0.5) -> float:
    """
    Normalize a score value to 0.0-1.0 range.
    
    Args:
        score: Score value (may be int, float, or string)
        default: Default value if normalization fails
    
    Returns:
        float: Normalized score between 0.0 and 1.0
    """
    try:
        score_float = float(score)
        
        # If score is 0-100 range, normalize to 0-1
        if score_float > 1.0:
            score_float = score_float / 100.0
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, score_float))
    except (ValueError, TypeError):
        return default


def extract_figure_references(text: str) -> list:
    """
    Extract figure references from patent text.
    
    Args:
        text: Patent text
    
    Returns:
        list: List of figure numbers (e.g., ["1", "2", "3A"])
    """
    # Pattern: FIG. 1, Figure 2, Fig.3A, etc.
    pattern = r'(?i)(?:fig(?:ure)?\.?\s*)(\d+[A-Z]?)'
    matches = re.findall(pattern, text)
    
    # Remove duplicates while preserving order
    seen = set()
    figures = []
    for fig in matches:
        if fig not in seen:
            seen.add(fig)
            figures.append(fig)
    
    return figures


def extract_element_references(text: str) -> list:
    """
    Extract element/reference numbers from patent text.
    
    Args:
        text: Patent text
    
    Returns:
        list: List of element numbers (e.g., ["10", "20", "100"])
    """
    # Pattern: element 10, reference numeral 20, numeral 100, etc.
    pattern = r'(?i)(?:element|reference\s+numeral|numeral)\s+(\d+)'
    matches = re.findall(pattern, text)
    
    # Remove duplicates
    return sorted(list(set(matches)))


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal value as percentage string.
    
    Args:
        value: Decimal value (0.0-1.0)
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage (e.g., "75.3%")
    """
    return f"{value * 100:.{decimals}f}%"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default on division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
    
    Returns:
        float: Result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default


def remove_margin_numbers(text: str) -> str:
    """
    Remove OCR'd margin line numbers (5, 10, 15, 20...) that pollute patent text.
    Handles numbers at the start of lines, or standalone multiples of 5 inline
    while protecting valid references like 'claim 5' or 'FIG. 10'.
    """
    if not text:
        return text
    
    # 1. Start-of-line margin numbers (e.g., "15 8. The system..." -> "8. The system...")
    text = re.sub(r'^(?:5|10|15|20|25|30|35|40|45|50|55|60|65|70|75|80)\s+', '', text, flags=re.MULTILINE)
    
    # 2. Inline margin numbers that got reflowed into the middle of sentences
    # Safe lookbehind ensures we don't delete legitimate patent numbered references
    safe_lookbehind = r'(?i)(?<!claim\s)(?<!claims\s)(?<!figure\s)(?<!fig\.\s)(?<!fig\s)(?<!element\s)(?<!numeral\s)'
    
    # Replace the isolated multiple-of-5 numbers
    pattern = fr'{safe_lookbehind}(?<![a-zA-Z0-9.-])\b(?:5|10|15|20|25|30|35|40|45|50|55|60|65|70|75|80)\b(?![a-zA-Z0-9.-])'
    text = re.sub(pattern, ' ', text)
    
    # Clean up double spaces caused by the removal
    text = re.sub(r' {2,}', ' ', text)
    
    return text

