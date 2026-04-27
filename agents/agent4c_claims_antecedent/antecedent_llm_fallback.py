"""
antecedent_llm_fallback.py
==========================
LLM fallback for ambiguous antecedent cases.
Uses Ollama for validation when spaCy analysis is inconclusive.
"""

import json
from typing import List, Dict, Any
from agents.claims_analyse_libs.core import OllamaClient
from agents.claims_analyse_libs.utils import parse_json_safe


ANTECEDENT_LLM_SYSTEM = """You are a senior EPO patent examiner. Analyze antecedent basis in patent claims.

DEFINITION:
- "the/said/this/that + noun" requires prior "a/an + noun" OR implicit introduction
- Singular/plural variants match: "plate" ≈ "plates", "top plate" ≈ "plate"
- Ignore generic terms: method, apparatus, system, device, invention
- Antecedent can be in same claim (earlier) OR any ancestor claim

Return ONLY valid JSON:
{
  "missing_antecedents": ["the actuator", "said housing"],
  "valid_antecedents": ["the plate"],
  "reasoning": "Brief explanation of analysis",
  "confidence": "high/medium/low"
}"""


def llm_validate_antecedents(
    claim_num: int,
    claim_text: str,
    ambiguous_terms: List[str],
    ancestor_texts: str,
    model_name: str = "gpt-oss:120b-cloud",
) -> Dict[str, Any]:
    """
    Use LLM to validate ambiguous antecedent cases.

    Args:
        claim_num: Claim number being analyzed
        claim_text: Full claim text
        ambiguous_terms: List of ambiguous definite references
        ancestor_texts: Combined text of ancestor claims
        model_name: Ollama model to use

    Returns:
        Dictionary with LLM analysis results
    """
    if not ambiguous_terms:
        return {
            "missing_antecedents": [],
            "valid_antecedents": [],
            "reasoning": "No ambiguous terms to validate",
            "confidence": "high",
        }

    client = OllamaClient(model_name=model_name)

    prompt = f"""Analyze antecedent basis for the following claim:

Claim {claim_num}: {claim_text}

Ambiguous definite references to validate: {", ".join(ambiguous_terms)}

Context from earlier claims:
{ancestor_texts[:2000] if ancestor_texts else "No earlier claims."}

For each ambiguous reference, determine if it has a proper antecedent.
Consider:
1. Same claim (earlier in text)
2. Ancestor claims (claims this depends on)
3. Implicit introductions (e.g., "comprising" introduces elements)

Return JSON with missing and valid antecedents."""

    try:
        response = client.generate(
            prompt=prompt,
            system_prompt=ANTECEDENT_LLM_SYSTEM,
            max_tokens=1000,
            temperature=0.1,
            response_format="json",
        )

        default = {
            "missing_antecedents": [],
            "valid_antecedents": [],
            "reasoning": "LLM validation failed",
            "confidence": "low",
        }

        return parse_json_safe(response, default)

    except Exception as e:
        print(f"⚠️ LLM validation failed: {e}")
        return {
            "missing_antecedents": ambiguous_terms,
            "valid_antecedents": [],
            "reasoning": f"LLM validation error: {str(e)}",
            "confidence": "low",
        }
