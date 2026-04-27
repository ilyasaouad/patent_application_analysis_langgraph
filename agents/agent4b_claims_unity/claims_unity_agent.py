"""
claims_unity_agent.py
=====================
LangGraph Agent Wrapper for Claims Unity Analysis

This is AGENT 4B - Continuation of the patent analysis pipeline.
Analyzes unity of independent claims under Norwegian Patents Act §10.

Input: Reads from output_text_documents/claims.md (and optionally description.md, drawings.md)
Output: Saves to output_clarity_analyse_report/
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from graph_state import GraphState
from agents.claims_analyse_libs.core import OllamaClient
from agents.claims_analyse_libs.utils import parse_json_safe, truncate_text
from .unity_prompts import UnityPrompts


# Directories
INPUT_DIR = Path("output_text_documents")
OUTPUT_DIR = Path("claims_analyse_reports/unity_analyse")
OUTPUT_DIR.mkdir(exist_ok=True)


def claims_unity_agent(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph-compatible agent for claims unity analysis.

    This is AGENT 4B - Continuation of patent analysis pipeline.
    Analyzes whether claims constitute a single invention or multiple
    mutually independent inventions under Norwegian Patents Act §10.

    Args:
        state: GraphState (uses claims_text, description_text, drawings_text)

    Returns:
        dict with claims_unity_results
    """
    print("\n" + "=" * 70)
    print("🔗 AGENT 4B: Claims Unity Analysis - NIPO § 10")
    print("=" * 70)
    print("This is a continuation of the patent analysis pipeline.")
    print("Analyzing unity of independent claims...")
    print("=" * 70 + "\n")

    # Try to get text from state first, otherwise read from files
    claims = state.get("claims_text", "")
    description = state.get("description_text", "")
    drawings = state.get("drawings_text", "")

    # If state is empty, read from output_text_documents/
    if not claims and INPUT_DIR.exists():
        claims_file = INPUT_DIR / "claims.md"
        if claims_file.exists():
            with open(claims_file, "r", encoding="utf-8") as f:
                claims = f.read()
            print(f"[Agent 4B] Loaded claims from {claims_file}")

    if not description and INPUT_DIR.exists():
        desc_file = INPUT_DIR / "description.md"
        if desc_file.exists():
            with open(desc_file, "r", encoding="utf-8") as f:
                description = f.read()
            print(f"[Agent 4B] Loaded description from {desc_file}")

    if not drawings and INPUT_DIR.exists():
        drawings_file = INPUT_DIR / "drawings.md"
        if drawings_file.exists():
            with open(drawings_file, "r", encoding="utf-8") as f:
                drawings = f.read()
            print(f"[Agent 4B] Loaded drawings from {drawings_file}")

    # Validate we have claims
    if not claims:
        error_msg = "Missing claims. Please run extraction first (Agent 1)."
        print(f"[Agent 4B] ERROR: {error_msg}")
        return {
            "claims_unity_results": {
                "status": "ERROR",
                "error": error_msg,
                "message": "Run the extraction pipeline first to generate output_text_documents/claims.md",
            }
        }

    try:
        # Initialize Ollama client
        client = OllamaClient(
            model_name="gpt-oss:120b-cloud",  # Default model
            base_url="http://localhost:11434",
        )

        # Test connection
        if not client.test_connection():
            raise ConnectionError("Cannot connect to Ollama for unity analysis")

        # Prepare prompt
        prompt = UnityPrompts.format_prompt(
            UnityPrompts.UNITY_USER,
            guidelines="Norwegian Patents Act §10 and Patent Regulations §8",
            claims=truncate_text(claims, 6000),
            description=truncate_text(description, 4000)
            if description
            else "Not provided",
            drawings=truncate_text(drawings, 2000) if drawings else "Not provided",
            preferred_grouping_hint="Not provided",
        )

        # Generate analysis
        print("[Agent 4B] Running unity analysis...")
        response = client.generate(
            prompt=prompt,
            system_prompt=UnityPrompts.UNITY_SYSTEM,
            max_tokens=2000,
            temperature=0.1,
            response_format="json",
        )

        # Parse JSON response
        default_result = {
            "conclusion": "SINGLE_INVENTION",
            "status_reason": "Analysis incomplete",
            "grouping": [],
            "common_features": [],
            "technical_relationship_analysis": "Analysis incomplete",
            "legal_mapping": "Norwegian Patents Act §10",
            "recommendation": "Manual review required",
            "confidence": "LOW",
            "exemplar_analogies_used": [],
            "guideline_version": "NIPO Unity Guidelines",
        }

        result_dict = parse_json_safe(response, default_result)
        result_dict["status"] = "SUCCESS"

        # Save results
        json_path = OUTPUT_DIR / "claims_unity_result.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"[Agent 4B] Results saved to {json_path}")

        # Generate human-readable report
        report_lines = []
        report_lines.append("# Claims Unity Analysis Report")
        report_lines.append("## Norwegian Patents Act §10 / Patent Regulations §8")
        report_lines.append("")
        report_lines.append(f"**Conclusion:** {result_dict.get('conclusion', 'N/A')}")
        report_lines.append(f"**Confidence:** {result_dict.get('confidence', 'N/A')}")
        report_lines.append("")
        report_lines.append(
            f"**Status Reason:** {result_dict.get('status_reason', '')}"
        )
        report_lines.append("")

        # Grouping
        grouping = result_dict.get("grouping", [])
        if grouping:
            report_lines.append("### Claim Grouping")
            for group in grouping:
                report_lines.append(f"\n**Group {group.get('group_no', 'N/A')}:**")
                report_lines.append(
                    f"- Representative Claims: {', '.join(group.get('representative_independent_claims', []))}"
                )
                report_lines.append(
                    f"- Technical Subject Matter: {group.get('technical_subject_matter', '')}"
                )
                report_lines.append(
                    f"- Objective Technical Problem: {group.get('objective_technical_problem', '')}"
                )
                report_lines.append(
                    f"- Special Technical Features: {', '.join(group.get('special_technical_features', []))}"
                )

        # Common features
        common = result_dict.get("common_features", [])
        if common:
            report_lines.append("\n### Common Features")
            for feat in common:
                report_lines.append(f"- {feat}")

        # Technical relationship
        analysis = result_dict.get("technical_relationship_analysis", "")
        if analysis:
            report_lines.append("\n### Technical Relationship Analysis")
            report_lines.append(analysis)

        # Legal mapping
        legal = result_dict.get("legal_mapping", "")
        if legal:
            report_lines.append("\n### Legal Mapping")
            report_lines.append(legal)

        # Recommendation
        rec = result_dict.get("recommendation", "")
        if rec:
            report_lines.append("\n### Recommendation")
            report_lines.append(rec)

        # Exemplars
        exemplars = result_dict.get("exemplar_analogies_used", [])
        if exemplars:
            report_lines.append("\n### Exemplar Analogies")
            for ex in exemplars:
                report_lines.append(f"\n**{ex.get('case_id', 'N/A')}:**")
                report_lines.append(f"- Summary: {ex.get('one_line_summary', '')}")
                report_lines.append(f"- Mapping: {ex.get('mapping', '')}")

        report_text = "\n".join(report_lines)

        # Save report
        report_path = OUTPUT_DIR / "claims_unity_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"[Agent 4B] Report saved to {report_path}")

        # Save rejection letter if multiple inventions
        if result_dict.get("conclusion") == "MULTIPLE_INVENTIONS":
            rejection_letter = result_dict.get("rejection_letter", "")
            if rejection_letter:
                rejection_path = OUTPUT_DIR / "claims_unity_rejection_letter.md"
                with open(rejection_path, "w", encoding="utf-8") as f:
                    f.write("# NIPO Unity Rejection Letter\n\n")
                    f.write("## Norwegian Patents Act §10 / Patent Regulations §8\n\n")
                    f.write(rejection_letter)
                print(f"[Agent 4B] Rejection letter saved to {rejection_path}")

        print("\n" + "=" * 70)
        print(
            f"✅ Agent 4B Complete: {result_dict.get('conclusion', 'N/A')} | Confidence: {result_dict.get('confidence', 'N/A')}"
        )
        print("=" * 70 + "\n")

        return {"claims_unity_results": result_dict}

    except Exception as e:
        print(f"[Agent 4B] CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {
            "claims_unity_results": {
                "status": "ERROR",
                "error": str(e),
                "message": "Failed to run claims unity analysis. Ensure Ollama is running.",
            }
        }


def run_claims_unity(
    claims: Optional[str] = None,
    description: Optional[str] = None,
    drawings: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Standalone function to run claims unity analysis.

    Args:
        claims: Patent claims text
        description: Patent description text (optional)
        drawings: Patent drawings text (optional)

    Returns:
        Analysis results dict
    """
    state = {
        "claims_text": claims or "",
        "description_text": description or "",
        "drawings_text": drawings or "",
    }
    return claims_unity_agent(state)
