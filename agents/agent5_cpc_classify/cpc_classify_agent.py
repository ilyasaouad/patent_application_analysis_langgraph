"""
Agent 5: CPC Classification

LangGraph node that classifies patents into CPC codes using the full 4-phase pipeline
ported from MCP_cpc_classes.
"""

import os
from typing import List
from graph_state import GraphState
from .classifier import CPCClassifier


def _extract_cpc_list(classification_result: dict) -> List[str]:
    """Extract flat list of CPC codes from classification result."""
    codes = []

    # Try phase4 best code first
    if "phase4" in classification_result:
        best = classification_result["phase4"].get("best_code", {})
        if best and "symbol" in best:
            codes.append(best["symbol"])

    # Fall back to phase3 ranked codes
    if not codes and "phase3" in classification_result:
        for node in classification_result["phase3"]:
            if "symbol" in node:
                codes.append(node["symbol"])

    # Fall back to phase2
    if not codes and "phase2" in classification_result:
        codes = classification_result["phase2"].get("codes", [])

    # Fall back to phase1 suggested classes
    if not codes and "phase1" in classification_result:
        phase1 = classification_result["phase1"]
        if isinstance(phase1, dict):
            cpc_classes = phase1.get("cpc_classes", [])
            if cpc_classes:
                codes = cpc_classes

    return codes


def cpc_classify_agent(state: GraphState) -> GraphState:
    """
    LangGraph Node: Classify patent into CPC classes using the full 4-phase pipeline.

    Input from state: description_text, claims_text
    Output to state: cpc_classes (List[str]), cpc_classification (dict with full results)
    """
    description = state.get("description_text", "")
    claims = state.get("claims_text", "")

    print("[CPC Classify Agent] Starting CPC classification...")

    if not description and not claims:
        print("[CPC Classify Agent] No text available for classification.")
        return {
            "cpc_classes": [],
            "cpc_classification": None,
            "status": "ERROR",
            "error_message": "No description or claims text available for CPC classification.",
        }

    try:
        classifier = CPCClassifier()
        result = classifier.classify(description, claims)

        # Extract simple list for downstream agents
        cpc_list = _extract_cpc_list(result)

        print(f"[CPC Classify Agent] Classified into: {cpc_list}")

        return {
            "cpc_classes": cpc_list,
            "cpc_classification": result,
            "status": "SUCCESS",
        }

    except Exception as e:
        print(f"[CPC Classify Agent] Error during classification: {e}")
        return {
            "cpc_classes": [],
            "cpc_classification": None,
            "status": "ERROR",
            "error_message": str(e),
        }
