"""
claims_clarity_agent.py
=======================
LangGraph Agent Wrapper for Claims Clarity Analysis

This is AGENT 4 - Continuation of the patent analysis pipeline.
It reads extracted text from output_text_documents/ and performs
legal analysis for enablement, clarity, and support (NIPO § 8).

Input: Reads from output_text_documents/description.md, claims.md, drawings.md
Output: Saves to output_analysis_reports/
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

from graph_state import GraphState
from .claims_legal_analyzer import PatentLegalAnalyzer
from agents.claims_analyse_libs.config import AnalyzerConfig


# Directories
INPUT_DIR = Path("output_text_documents")
OUTPUT_DIR = Path("claims_analyse_reports/clarity_analyse")
OUTPUT_DIR.mkdir(exist_ok=True)


def claims_clarity_agent(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph-compatible agent for claims clarity legal analysis.

    This is AGENT 4 - Continuation of patent analysis pipeline.
    Reads extracted text files and performs NIPO legal analysis.

    Args:
        state: GraphState (uses description_text, claims_text, drawings_text if available,
               otherwise reads from output_text_documents/)

    Returns:
        dict with claims_clarity_results
    """
    print("\n" + "=" * 70)
    print("⚖️  AGENT 4: Claims Clarity Analysis - NIPO § 8")
    print("=" * 70)
    print("This is a continuation of the patent analysis pipeline.")
    print("Reading extracted documents from output_text_documents/")
    print("=" * 70 + "\n")

    # Try to get text from state first, otherwise read from files
    description = state.get("description_text", "")
    claims = state.get("claims_text", "")
    drawings = state.get("drawings_text", "")

    # If state is empty, read from output_text_documents/
    if not description and INPUT_DIR.exists():
        desc_file = INPUT_DIR / "description.md"
        if desc_file.exists():
            with open(desc_file, "r", encoding="utf-8") as f:
                description = f.read()
            print(f"[Agent 4] Loaded description from {desc_file}")

    if not claims and INPUT_DIR.exists():
        claims_file = INPUT_DIR / "claims.md"
        if claims_file.exists():
            with open(claims_file, "r", encoding="utf-8") as f:
                claims = f.read()
            print(f"[Agent 4] Loaded claims from {claims_file}")

    if not drawings and INPUT_DIR.exists():
        drawings_file = INPUT_DIR / "drawings.md"
        if drawings_file.exists():
            with open(drawings_file, "r", encoding="utf-8") as f:
                drawings = f.read()
            print(f"[Agent 4] Loaded drawings from {drawings_file}")

    # Validate we have required files
    if not claims or not description:
        error_msg = "Missing required files. Please run extraction first (Agent 1)."
        print(f"[Agent 4] ERROR: {error_msg}")
        return {
            "claims_clarity_results": {
                "status": "ERROR",
                "error": error_msg,
                "message": "Run the extraction pipeline first to generate output_text_documents/*.md files",
            }
        }

    try:
        # Initialize analyzer
        config = AnalyzerConfig()
        analyzer = PatentLegalAnalyzer(config=config)

        # Run analysis
        print("[Agent 4] Starting legal analysis...")
        result = analyzer.analyze(
            claims=claims,
            description=description,
            drawings=drawings if drawings else None,
        )

        # Convert to dict for state storage
        result_dict = {
            "status": "SUCCESS",
            "enablement": {
                "status": result.enablement.status,
                "status_reason": result.enablement.status_reason,
                "issues": result.enablement.issues,
                "missing_elements": result.enablement.missing_elements,
                "technical_deficiencies": result.enablement.technical_deficiencies,
                "reproducibility_score": result.enablement.reproducibility_score,
                "confidence": result.enablement.confidence,
            },
            "clarity": {
                "status": result.clarity.status,
                "status_reason": result.clarity.status_reason,
                "issues": result.clarity.issues,
                "vague_terms": result.clarity.vague_terms,
                "undefined_terms": result.clarity.undefined_terms,
                "ambiguous_phrases": result.clarity.ambiguous_phrases,
                "clarity_score": result.clarity.clarity_score,
                "confidence": result.clarity.confidence,
            },
            "support": {
                "status": result.support.status,
                "status_reason": result.support.status_reason,
                "issues": result.support.issues,
                "unsupported_elements": result.support.unsupported_elements,
                "broader_than_description": result.support.broader_than_description,
                "missing_embodiments": result.support.missing_embodiments,
                "support_score": result.support.support_score,
                "confidence": result.support.confidence,
            },
            "overall": {
                "risk_level": result.risk_level,
                "summary": result.summary,
                "critical_issues": result.critical_issues,
                "recommendations": result.recommendations,
                "examination_decision": result.examination_decision,
            },
            "formal_report": result.formal_report,
        }

        # Save results to output_analysis_reports/
        import json

        # Save JSON
        json_path = OUTPUT_DIR / "claims_clarity_result.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"[Agent 4] Results saved to {json_path}")

        # Save formal report as markdown
        if result.formal_report:
            report_path = OUTPUT_DIR / "claims_clarity_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("# Claims Clarity Analysis Report\n\n")
                f.write("## NIPO Patent Examination - § 8 Analysis\n\n")
                f.write(result.formal_report)
                f.write("\n\n---\n\n")
                f.write("## Summary\n\n")
                f.write(f"**Examination Decision:** {result.examination_decision}\n\n")
                f.write(f"**Risk Level:** {result.risk_level}\n\n")
                f.write(f"**Critical Issues:**\n")
                for issue in result.critical_issues:
                    f.write(f"- {issue}\n")
                f.write("\n**Recommendations:**\n")
                for rec in result.recommendations:
                    f.write(f"- {rec}\n")
            print(f"[Agent 4] Report saved to {report_path}")

        print("\n" + "=" * 70)
        print(
            f"✅ Agent 4 Complete: {result.examination_decision} | Risk: {result.risk_level}"
        )
        print("=" * 70 + "\n")

        return {"claims_clarity_results": result_dict}

    except Exception as e:
        print(f"[Agent 4] CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {
            "claims_clarity_results": {
                "status": "ERROR",
                "error": str(e),
                "message": "Failed to run claims clarity analysis. Ensure Ollama is running.",
            }
        }


def run_claims_clarity(
    description: Optional[str] = None,
    claims: Optional[str] = None,
    drawings: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Standalone function to run claims clarity analysis.

    Args:
        description: Patent description text
        claims: Patent claims text
        drawings: Patent drawings text (optional)

    Returns:
        Analysis results dict
    """
    state = {
        "description_text": description or "",
        "claims_text": claims or "",
        "drawings_text": drawings or "",
    }
    return claims_clarity_agent(state)
