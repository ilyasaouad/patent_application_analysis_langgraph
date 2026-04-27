"""
ai_generated_detection_agent.py
==============================
LangGraph Agent Wrapper for AI Patent Detection

This agent analyzes patent documents for AI-generated content indicators.
It runs independently and takes extracted text from agent1_read_parse_document.

Usage:
    from agents.agent2b_ai_generated_document.ai_generated_detection_agent import ai_generated_detection_agent

    result = ai_generated_detection_agent(state)
"""

from typing import Dict, Any, Optional
from graph_state import GraphState

# Import the analyzer components
from .ai_patent_analyzer import AIPatentAnalyzer
from .ai_detection_summarizer import (
    generate_ai_detection_summary,
    generate_brief_summary,
)
from .config import AnalyzerConfig
from .core import DetectionResult


def ai_generated_detection_agent(state: GraphState) -> GraphState:
    """
    LangGraph-compatible agent for AI-generated content detection.

    Takes patent text from state (description, claims, drawings) and runs
    multi-phase AI detection analysis.

    Args:
        state: GraphState containing extracted patent texts

    Returns:
        GraphState update dict with ai_detection_results
    """
    print("[AI Generated Detection Agent] Starting analysis...")

    # Extract texts from state
    description = state.get("description_text", "") or ""
    claims = state.get("claims_text", "") or ""
    drawings = state.get("drawings_text", "") or ""

    # Check if we have any text to analyze
    if not description and not claims:
        print("[AI Generated Detection Agent] No text available for analysis")
        return {
            "ai_detection_results": {
                "error": "No patent text available for analysis",
                "status": "ERROR",
            }
        }

    try:
        # Initialize analyzer with default config
        config = AnalyzerConfig()
        analyzer = AIPatentAnalyzer(config=config)

        # Run analysis directly with text (no directory needed)
        print(f"[AI Generated Detection Agent] Running analysis on:")
        print(f"  - Description: {len(description)} chars")
        print(f"  - Claims: {len(claims)} chars")
        print(f"  - Drawings: {len(drawings)} chars")

        result = analyzer.analyze_text(
            text=description,
            claims=claims if claims else None,
            drawings=drawings if drawings else None,
        )

        # Convert DetectionResult to dict for state storage
        result_dict = result.to_dict()
        result_dict["status"] = "SUCCESS"

        # Generate human-readable summary
        result_dict["summary"] = generate_ai_detection_summary(result_dict)
        result_dict["brief_summary"] = generate_brief_summary(result_dict)

        print(
            f"[AI Generated Detection Agent] Analysis complete: {result.get_summary()}"
        )

        return {"ai_detection_results": result_dict}

    except Exception as e:
        print(f"[AI Generated Detection Agent] ERROR: {e}")
        return {"ai_detection_results": {"error": str(e), "status": "ERROR"}}


def run_ai_detection(
    description: Optional[str] = None,
    claims: Optional[str] = None,
    drawings: Optional[str] = None,
) -> DetectionResult:
    """
    Standalone function to run AI detection on patent text.

    Can be called directly without going through LangGraph.

    Args:
        description: Patent description text
        claims: Patent claims text
        drawings: Patent drawings text

    Returns:
        DetectionResult with analysis results
    """
    config = AnalyzerConfig()
    analyzer = AIPatentAnalyzer(config=config)

    return analyzer.analyze_text(
        text=description or "", claims=claims, drawings=drawings
    )
