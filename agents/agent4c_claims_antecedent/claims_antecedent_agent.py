"""
claims_antecedent_agent.py
==========================
LangGraph Agent Wrapper for Claims Antecedent Basis Analysis

This is AGENT 4C - Continuation of the patent analysis pipeline.
Analyzes claims for antecedent basis using spaCy NLP + LLM fallback.

Input: Reads from output_text_documents/claims.md
Output: Saves to claims_analyse_reports/antecedent_analyse/
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from graph_state import GraphState
from .antecedent_NLP_analyzer import AntecedentAnalyzer, Claim
from .antecedent_llm_fallback import llm_validate_antecedents
from agents.claims_analyse_libs.core import OllamaClient


# Directories
INPUT_DIR = Path("output_text_documents")
OUTPUT_DIR = Path("claims_analyse_reports/antecedent_analyse")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def claims_antecedent_agent(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph-compatible agent for claims antecedent basis analysis.

    This is AGENT 4C - Continuation of patent analysis pipeline.
    Uses spaCy NLP for primary detection, LLM for ambiguous cases.

    Args:
        state: GraphState (uses claims_text if available,
               otherwise reads from output_text_documents/)

    Returns:
        dict with claims_antecedent_results
    """
    print("\n" + "=" * 70)
    print("🔗 AGENT 4C: Claims Antecedent Basis Analysis")
    print("=" * 70)
    print("This is a continuation of the patent analysis pipeline.")
    print("Analyzing antecedent basis in claims using spaCy NLP...")
    print("=" * 70 + "\n")

    # Try to get claims from state first
    claims_text = state.get("claims_text", "")

    # If state is empty, read from file
    if not claims_text and INPUT_DIR.exists():
        claims_file = INPUT_DIR / "claims.md"
        if claims_file.exists():
            with open(claims_file, "r", encoding="utf-8") as f:
                claims_text = f.read()
            print(f"[Agent 4C] Loaded claims from {claims_file}")

    # Validate we have claims
    if not claims_text:
        error_msg = "Missing claims. Please run extraction first (Agent 1)."
        print(f"[Agent 4C] ERROR: {error_msg}")
        return {
            "claims_antecedent_results": {
                "status": "ERROR",
                "error": error_msg,
                "message": "Run the extraction pipeline first to generate output_text_documents/claims.md",
            }
        }

    try:
        # Initialize analyzer
        analyzer = AntecedentAnalyzer(use_spacy=True)

        # Run primary analysis
        print("[Agent 4C] Running spaCy antecedent analysis...")
        results = analyzer.analyze_all_claims(claims_text)

        if results["status"] == "ERROR":
            return {"claims_antecedent_results": results}

        # LLM fallback for ambiguous cases
        print("[Agent 4C] Checking for ambiguous cases...")
        claims = analyzer._parse_claims(claims_text)

        # Process ambiguous terms with LLM
        llm_issues = []
        for claim in claims:
            ambiguous = analyzer.get_ambiguous_terms(claim)
            if ambiguous:
                # Get ancestor texts
                ancestors = analyzer._find_ancestor_claims(claim, claims)
                ancestor_text = "\n".join(
                    [f"Claim {c.number}: {c.text[:200]}" for c in ancestors]
                )

                # LLM validation
                llm_result = llm_validate_antecedents(
                    claim_num=claim.number,
                    claim_text=claim.text,
                    ambiguous_terms=ambiguous,
                    ancestor_texts=ancestor_text,
                )

                # Add LLM-confirmed missing antecedents
                for term in llm_result.get("missing_antecedents", []):
                    llm_issues.append(
                        {
                            "claim_number": claim.number,
                            "term": term,
                            "definite_reference": term,
                            "context": analyzer._get_context(claim.text, term),
                            "confidence": llm_result.get("confidence", "medium"),
                            "reasoning": f"LLM validation: {llm_result.get('reasoning', '')}",
                        }
                    )

        # Merge spaCy and LLM results
        all_issues = results.get("issues", []) + llm_issues

        # Deduplicate
        seen = set()
        unique_issues = []
        for issue in all_issues:
            key = (issue["claim_number"], issue["term"].lower())
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        # Update results
        results["issues"] = unique_issues
        results["issues_found"] = len(unique_issues)
        results["llm_validated"] = len(llm_issues)
        results["status"] = "SUCCESS"

        # Save results
        json_path = OUTPUT_DIR / "claims_antecedent_result.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[Agent 4C] Results saved to {json_path}")

        # Generate human-readable report
        report_lines = []
        report_lines.append("# Claims Antecedent Basis Analysis Report")
        report_lines.append("## Patent Examination - Antecedent Basis Check")
        report_lines.append("")
        report_lines.append(f"**Total Claims Analyzed:** {results['claim_count']}")
        report_lines.append(f"**Issues Found:** {results['issues_found']}")
        report_lines.append(f"**Claims with Issues:** {results['claims_with_issues']}")
        report_lines.append(f"**LLM Validated:** {results['llm_validated']}")
        report_lines.append("")

        if unique_issues:
            report_lines.append("### Antecedent Basis Issues")
            report_lines.append("")

            # Group by claim
            from collections import defaultdict

            claim_issues = defaultdict(list)
            for issue in unique_issues:
                claim_issues[issue["claim_number"]].append(issue)

            for claim_num in sorted(claim_issues.keys()):
                report_lines.append(f"**Claim {claim_num}:**")
                for issue in claim_issues[claim_num]:
                    report_lines.append(f"- ❌ **{issue['definite_reference']}**")
                    report_lines.append(f"  - Reasoning: {issue['reasoning']}")
                    report_lines.append(f"  - Confidence: {issue['confidence']}")
                    if issue.get("context"):
                        report_lines.append(
                            f"  - Context: ...{issue['context'][:100]}..."
                        )
                report_lines.append("")
        else:
            report_lines.append("✅ **No antecedent basis issues found.**")

        report_text = "\n".join(report_lines)

        # Save report
        report_path = OUTPUT_DIR / "claims_antecedent_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"[Agent 4C] Report saved to {report_path}")

        print("\n" + "=" * 70)
        print(
            f"✅ Agent 4C Complete: {results['issues_found']} issues | LLM: {results['llm_validated']}"
        )
        print("=" * 70 + "\n")

        return {"claims_antecedent_results": results}

    except Exception as e:
        print(f"[Agent 4C] CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {
            "claims_antecedent_results": {
                "status": "ERROR",
                "error": str(e),
                "message": "Failed to run antecedent analysis. Ensure spaCy and Ollama are available.",
            }
        }


def run_antecedent_analysis(claims: Optional[str] = None) -> Dict[str, Any]:
    """
    Standalone function to run antecedent basis analysis.

    Args:
        claims: Patent claims text

    Returns:
        Analysis results dict
    """
    state = {
        "claims_text": claims or "",
        "description_text": "",
        "drawings_text": "",
    }
    return claims_antecedent_agent(state)
