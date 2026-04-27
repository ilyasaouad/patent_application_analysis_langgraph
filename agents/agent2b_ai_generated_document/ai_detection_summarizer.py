"""
ai_detection_summarizer.py
===========================
Generates human-readable summaries of AI detection results.

Follows the exact structure requested by the user:
- Clear, plain English explanations
- Interprets rather than repeats raw data
- Distinguishes AI detection vs technical quality vs legal sufficiency
- Professional but conversational tone
- Does NOT say "the model says" — speaks directly
- Does NOT copy phrases from input — interprets them
- Does NOT overstate certainty
"""

from typing import Dict, Any, List


def generate_ai_detection_summary(ai_results: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of AI detection results.

    Args:
        ai_results: The ai_detection_results dictionary from state

    Returns:
        str: Formatted summary following the required structure
    """
    if not ai_results or ai_results.get("status") == "ERROR":
        return "The analysis could not be completed. Please check that your documents were properly extracted and try again."

    is_ai = ai_results.get("is_likely_ai_generated", False)
    confidence = ai_results.get("confidence_score", 0)
    risk_level = ai_results.get("risk_level", "UNKNOWN")
    feature_scores = ai_results.get("feature_scores", {})
    detailed = ai_results.get("detailed_analysis", {})
    recommendations = ai_results.get("recommendations", [])

    # Extract sub-analyses
    fingerprint = detailed.get("fingerprint_analysis", {})
    anchor = detailed.get("anchor_analysis", {})
    hallucination = detailed.get("hallucination_analysis", {})
    drawing = detailed.get("drawing_analysis", {})
    enablement = detailed.get("enablement_assessment", {})

    lines = []

    # ========================================================================
    # 🧠 1. Bottom line: Is it AI-generated?
    # ========================================================================
    lines.append("## 🧠 1. Bottom Line: Is it AI-generated?")
    lines.append("")

    if is_ai:
        if confidence >= 0.75:
            lines.append("**Conclusion: YES — This document is likely AI-generated.**")
            lines.append(
                f"The confidence level is high at **{confidence:.1%}**, meaning multiple independent signals all point toward AI authorship."
            )
        else:
            lines.append(
                "**Conclusion: LIKELY YES — This document shows AI generation indicators.**"
            )
            lines.append(
                f"The confidence level is **{confidence:.1%}**, which sits in a gray zone. While several signals suggest AI involvement, the evidence is not overwhelming."
            )
    else:
        if confidence <= 0.25:
            lines.append(
                "**Conclusion: NO — This document appears to be human-written.**"
            )
            lines.append(
                f"The confidence level is low at **{confidence:.1%}**, meaning very few AI indicators were found."
            )
        else:
            lines.append(
                "**Conclusion: LIKELY NO — This document appears human-written.**"
            )
            lines.append(
                f"The confidence level is **{(1 - confidence):.1%}** in favor of human authorship, though a few minor patterns were detected."
            )

    # Gray zone clarification
    if 0.5 <= confidence <= 0.75 and is_ai:
        lines.append(
            "This falls into a **gray zone** — the indicators are present but not definitive. The document may be AI-assisted rather than fully AI-generated, or it may simply use very formal, structured language typical of patents."
        )
    elif 0.25 <= confidence <= 0.5 and not is_ai:
        lines.append(
            "This is approaching a **gray zone** — while the overall signal points to human authorship, there are enough minor patterns that some AI assistance cannot be completely ruled out."
        )

    lines.append("")

    # ========================================================================
    # ⚖️ 2. Risk Level Interpretation
    # ========================================================================
    lines.append("## ⚖️ 2. Risk Level Interpretation")
    lines.append("")

    if risk_level == "HIGH":
        lines.append("**Risk Level: HIGH**")
        lines.append(
            "This means the document shows **strong and consistent patterns** that match known AI generation behaviors. Multiple independent checks all flagged similar concerns."
        )
        lines.append(
            "In practice, this suggests the text may have been produced — or heavily assisted — by a large language model. The language is likely too uniform, too templated, or lacks the natural variation typical of human writing."
        )
    elif risk_level == "MEDIUM":
        lines.append("**Risk Level: MEDIUM**")
        lines.append(
            "This means the document shows **moderate AI indicators**. Some patterns look machine-generated, but others appear natural."
        )
        lines.append("In practice, this could mean:")
        lines.append("- The document was AI-generated but then edited by a human")
        lines.append(
            "- The document uses very formal patent language that happens to trigger some detectors"
        )
        lines.append(
            "- Only certain sections (like the abstract or background) are AI-generated"
        )
    elif risk_level == "LOW":
        lines.append("**Risk Level: LOW**")
        lines.append(
            "This means the document shows **few AI indicators**. Most of the text reads naturally, with only minor patterns that could be attributed to AI."
        )
        lines.append(
            "In practice, this is typical of well-written human-authored patents. The minor flags are likely just stylistic choices or standard legal phrasing."
        )
    elif risk_level == "MINIMAL":
        lines.append("**Risk Level: MINIMAL**")
        lines.append(
            "This means **no significant AI signals** were detected. The text shows natural variation, personal style, and technical depth consistent with human authorship."
        )
    else:
        lines.append(f"**Risk Level: {risk_level}**")
        lines.append(
            "The risk level could not be clearly determined. Please review the detailed scores below."
        )

    lines.append("")

    # ========================================================================
    # 🔍 3. Key Driver Explanation
    # ========================================================================
    lines.append("## 🔍 3. Key Driver Explanation")
    lines.append("")

    anchor_sim = anchor.get("similarity", 0.5)

    lines.append("**Primary Detection Method: Anchor Comparison**")
    lines.append("")
    lines.append(
        "This method works by asking an AI to write a patent description based *only* on the claims, then comparing that AI-generated text to the actual document. If they are very similar, it suggests the original was also AI-generated."
    )
    lines.append("")

    if anchor_sim >= 0.80:
        lines.append(f"**Anchor Similarity Score: {anchor_sim:.1%} (Very High)**")
        lines.append(
            "The AI-generated anchor text was **very similar** to the original document. This is a strong signal because:"
        )
        lines.append(
            "- AI models tend to produce consistent, templated language when given the same technical input"
        )
        lines.append(
            "- The original description follows the same predictable patterns as the AI-generated version"
        )
        lines.append(
            "- This level of similarity is unlikely to occur by chance with human writing"
        )
    elif anchor_sim >= 0.60:
        lines.append(f"**Anchor Similarity Score: {anchor_sim:.1%} (High)**")
        lines.append(
            "The AI-generated anchor text was **noticeably similar** to the original. While not definitive, this suggests:"
        )
        lines.append("- The original may have been AI-generated or heavily AI-assisted")
        lines.append(
            "- The writing follows standard templates and predictable structures"
        )
        lines.append("- Human editing may have been applied to an AI-generated draft")
    elif anchor_sim >= 0.40:
        lines.append(f"**Anchor Similarity Score: {anchor_sim:.1%} (Moderate)**")
        lines.append(
            "The AI-generated anchor and the original document share **some structural similarities**, but they are not close enough to strongly suggest AI authorship. This is a weak signal."
        )
    else:
        lines.append(f"**Anchor Similarity Score: {anchor_sim:.1%} (Low)**")
        lines.append(
            "The AI-generated anchor was **quite different** from the original document. This suggests:"
        )
        lines.append("- The original was likely written by a human with a unique style")
        lines.append(
            "- The description contains specific details and phrasing that the AI did not reproduce"
        )
        lines.append("- This is a strong indicator against AI generation")

    lines.append("")

    # ========================================================================
    # 🤖 4. Hallucination / Language Analysis
    # ========================================================================
    lines.append("## 🤖 4. Hallucination & Language Analysis")
    lines.append("")

    hall_score = hallucination.get("score", 0.5)
    hall_findings = hallucination.get("findings", [])

    if hall_score >= 0.70:
        lines.append("**Hallucination / Unsupported Content: HIGH**")
        lines.append(
            "The description contains **technical terms or concepts that are not supported by the claims**. This means the document describes things that are not actually claimed — a common issue in AI-generated text where the model produces plausible-sounding but technically shallow content."
        )
        if hall_findings:
            lines.append("Examples of unsupported content:")
            for finding in hall_findings[:3]:
                lines.append(f"- {finding}")
    elif hall_score >= 0.50:
        lines.append("**Hallucination / Unsupported Content: MODERATE**")
        lines.append(
            "Some technical language in the description does not align well with the claims. This could indicate:"
        )
        lines.append(
            "- AI-generated filler text that sounds technical but lacks substance"
        )
        lines.append("- Poorly integrated copy-paste sections")
        lines.append("- Unclear claim scope leading to mismatched description")
    else:
        lines.append("**Hallucination / Unsupported Content: LOW**")
        lines.append(
            "The description aligns well with the claims. Technical terms are properly supported, and there is minimal unsupported content."
        )

    lines.append("")
    lines.append(
        "**Important Note:** High hallucination scores do **not** automatically mean the text is AI-generated. Human writers can also include unsupported technical details. However, excessive unsupported content is a **quality issue** regardless of authorship — it weakens the patent and may cause problems during examination."
    )
    lines.append("")

    # Language style from fingerprint
    fp_score = feature_scores.get("fingerprint", 0.5)
    fp_findings = fingerprint.get("findings", [])

    if fp_score >= 0.60:
        lines.append("**Writing Style: Shows AI-like patterns**")
        lines.append(
            "The text exhibits stylistic markers often seen in AI-generated content:"
        )
        if fp_findings:
            for finding in fp_findings[:3]:
                lines.append(f"- {finding}")
        else:
            lines.append("- Uniform sentence structures")
            lines.append("- Repetitive transitions (e.g., 'Furthermore', 'Moreover')")
            lines.append("- Overly formal or generic phrasing")
    elif fp_score <= 0.40:
        lines.append("**Writing Style: Natural variation detected**")
        lines.append(
            "The text shows human-like variation in sentence length, vocabulary, and structure. This is a good sign for authenticity."
        )
    else:
        lines.append("**Writing Style: Mixed patterns**")
        lines.append(
            "Some sections show natural variation, while others appear more uniform. This could indicate AI-assisted writing with human editing."
        )

    lines.append("")

    # ========================================================================
    # ⚠️ 5. Critical Issues (VERY IMPORTANT)
    # ========================================================================
    lines.append("## ⚠️ 5. Critical Issues")
    lines.append("")

    enablement_conclusion = enablement.get("enablement_conclusion", "UNCLEAR")
    missing_elements = enablement.get("missing_elements", [])
    tech_deficiencies = enablement.get("technical_deficiencies", [])

    if enablement_conclusion == "NOT ENABLED":
        lines.append("**🚨 ENABLEMENT ISSUE DETECTED — This is legally significant.**")
        lines.append("")
        lines.append(
            "The patent disclosure **does not provide enough detail** for a person skilled in the art to actually build or use the invention. This is called a **lack of enablement**, and it is one of the most common reasons patents are rejected or invalidated."
        )
        lines.append("")
        lines.append("**What this means in simple terms:**")
        lines.append(
            "- Someone reading your patent cannot figure out how to make your invention work"
        )
        lines.append(
            "- The description is too vague, too abstract, or skips important technical steps"
        )
        lines.append("- This makes the patent legally weak and easy to challenge")
        lines.append("")

        if missing_elements:
            lines.append("**Specific elements missing from the disclosure:**")
            for elem in missing_elements[:5]:
                lines.append(f"- {elem}")
            lines.append("")

        if tech_deficiencies:
            lines.append("**Technical deficiencies identified:**")
            for defic in tech_deficiencies[:5]:
                lines.append(f"- {defic}")
            lines.append("")

        lines.append("**Why this matters:**")
        lines.append(
            "A patent that is not enabled is **legally invalid**. Even if your invention is completely new and inventive, you will not get a granted patent — or if you do, it can be easily invalidated in court or opposition proceedings."
        )
        lines.append("")
        lines.append(
            "**This is a technical/legal quality issue, not necessarily an AI detection issue.** Both human-written and AI-generated patents can have enablement problems. However, AI-generated text is more prone to this because models often produce plausible-sounding but technically shallow content."
        )

    elif enablement_conclusion == "ENABLED":
        lines.append("**✓ Enablement Check: PASSED**")
        lines.append(
            "The disclosure provides sufficient technical detail for implementation. This is a positive sign for patent strength."
        )
    else:
        lines.append("**Enablement Check: UNCLEAR**")
        lines.append(
            "The analysis could not definitively determine whether the disclosure is sufficient. This is not a red flag, but a manual review by a patent attorney is recommended."
        )

    lines.append("")

    # ========================================================================
    # 📉 6. Feature Scores Breakdown
    # ========================================================================
    lines.append("## 📉 6. Feature Scores Breakdown")
    lines.append("")
    lines.append("Here is what each score means:")
    lines.append("")

    fp_score = feature_scores.get("fingerprint", 0.5)
    anchor_score = feature_scores.get("anchor_similarity", 0.5)
    hall_score_feat = feature_scores.get("hallucination", 0.5)
    draw_score = feature_scores.get("drawing", 0.5)

    # Fingerprint
    lines.append(f"**• Fingerprint Score: {fp_score:.1%} (Weight: 30%)**")
    if fp_score >= 0.60:
        lines.append(
            "  → The text shows uniform sentence structures, repetitive transitions, and generic phrasing — patterns typical of AI-generated content."
        )
    elif fp_score <= 0.40:
        lines.append(
            "  → The text shows natural variation in style, vocabulary, and sentence structure."
        )
    else:
        lines.append("  → Mixed patterns: some natural variation, some uniformity.")
    lines.append("")

    # Anchor
    lines.append(f"**• Anchor Similarity: {anchor_score:.1%} (Weight: 40%)**")
    if anchor_score >= 0.75:
        lines.append(
            "  → Very high similarity with AI-generated anchor. Strong signal that the original is AI-generated."
        )
    elif anchor_score >= 0.50:
        lines.append(
            "  → Moderate similarity. The original may be AI-assisted or follow standard templates."
        )
    else:
        lines.append(
            "  → Low similarity. The original differs significantly from AI-generated text."
        )
    lines.append("")

    # Hallucination
    lines.append(f"**• Hallucination Score: {hall_score_feat:.1%} (Weight: 20%)**")
    if hall_score_feat >= 0.60:
        lines.append(
            "  → The description contains unsupported technical content not found in the claims."
        )
    elif hall_score_feat <= 0.40:
        lines.append(
            "  → Good alignment between claims and description. Technical content is well-supported."
        )
    else:
        lines.append(
            "  → Some minor unsupported content, but within acceptable bounds."
        )
    lines.append("")

    # Drawing
    lines.append(f"**• Drawing Score: {draw_score:.1%} (Weight: 10%)**")
    if draw_score >= 0.60:
        lines.append(
            "  → The description references figures or elements that do not match the actual drawings."
        )
    elif draw_score <= 0.40:
        lines.append("  → The description aligns well with the drawings.")
    else:
        lines.append(
            "  → Minor inconsistencies or no drawings provided for comparison."
        )
    lines.append("")

    # ========================================================================
    # 🧾 7. Additional Warnings
    # ========================================================================
    lines.append("## 🧾 7. Additional Warnings")
    lines.append("")

    draw_findings = drawing.get("findings", [])
    has_drawing_warnings = any(
        "WARNING" in str(f) or "drawing" in str(f).lower() for f in draw_findings
    )

    if has_drawing_warnings:
        lines.append("**⚠️ Drawing References Detected but No Drawing File Provided**")
        lines.append(
            "The description explicitly references figures, drawings, or diagrams, but no drawing file was uploaded. This means:"
        )
        lines.append("- The AI detection analysis for drawings could not be completed")
        lines.append("- The patent application may be incomplete without the drawings")
        lines.append("- Figure references in the description cannot be verified")
        lines.append(
            "- For a complete analysis, please upload the drawing file if available"
        )
    else:
        lines.append(
            "No additional warnings. The document appears complete for analysis."
        )

    lines.append("")

    # ========================================================================
    # 🧠 Final Interpretation
    # ========================================================================
    lines.append("---")
    lines.append("## 🧠 Final Interpretation")
    lines.append("")

    # AI likelihood
    if confidence >= 0.75:
        lines.append(
            "**AI Likelihood: HIGH** — The document is very likely AI-generated based on multiple consistent signals."
        )
    elif confidence >= 0.50:
        lines.append(
            "**AI Likelihood: MODERATE** — The document shows several AI indicators, but the evidence is not conclusive. It may be AI-assisted or use highly formal language."
        )
    elif confidence >= 0.25:
        lines.append(
            "**AI Likelihood: LOW** — The document appears mostly human-written with only minor patterns that could be AI-related."
        )
    else:
        lines.append(
            "**AI Likelihood: VERY LOW** — The document shows strong signs of human authorship."
        )

    lines.append("")

    # Writing quality
    if fp_score >= 0.60 or hall_score >= 0.60:
        lines.append(
            "**Writing Quality: CONCERNING** — The text shows signs of low-quality generation, including unsupported technical content and uniform language patterns. This needs attention regardless of whether it is AI-generated."
        )
    elif fp_score <= 0.40 and hall_score <= 0.40:
        lines.append(
            "**Writing Quality: GOOD** — The text is technically sound, well-supported, and shows natural variation."
        )
    else:
        lines.append(
            "**Writing Quality: MIXED** — Some sections are strong, while others need improvement."
        )

    lines.append("")

    # Legal/technical strength
    if enablement_conclusion == "NOT_ENABLED":
        lines.append(
            "**Legal/Technical Strength: WEAK** — The enablement issue is a serious legal risk. Without sufficient technical detail, the patent cannot be enforced and may be rejected."
        )
    elif enablement_conclusion == "ENABLED":
        lines.append(
            "**Legal/Technical Strength: STRONG** — The disclosure is technically sufficient and legally sound."
        )
    else:
        lines.append(
            "**Legal/Technical Strength: UNCLEAR** — The technical sufficiency could not be fully assessed. A manual review is recommended."
        )

    lines.append("")

    # ========================================================================
    # 🎯 Recommendations
    # ========================================================================
    lines.append("## 🎯 Recommendations")
    lines.append("")

    if recommendations:
        lines.append("Based on the analysis, here are the recommended next steps:")
        lines.append("")
        for rec in recommendations[:8]:
            lines.append(f"- {rec}")
    else:
        lines.append("- Review the technical disclosure for completeness")
        lines.append(
            "- Ensure all claimed elements are adequately described with specific details"
        )
        lines.append("- Consider adding concrete examples, embodiments, or use cases")
        lines.append("- If drawings are referenced, upload them for complete analysis")

    # Add specific recommendations based on findings
    lines.append("")
    lines.append("**General advice:**")
    if enablement_conclusion == "NOT_ENABLED":
        lines.append(
            "- **Priority:** Add specific algorithms, formulas, or step-by-step processes to the description"
        )
        lines.append("- Include at least one concrete example or embodiment")
        lines.append(
            "- Define technical terms precisely and explain how components interact"
        )

    if hall_score >= 0.60:
        lines.append(
            "- Remove or support unsupported technical claims in the description"
        )
        lines.append(
            "- Ensure every technical term in the description is either claimed or clearly ancillary"
        )

    if fp_score >= 0.60:
        lines.append("- Vary sentence structure and length to improve readability")
        lines.append("- Replace generic transitions with more specific connectors")
        lines.append(
            "- Add specific technical details rather than broad generalizations"
        )

    lines.append("")
    lines.append("---")
    lines.append(
        "*This analysis is generated by an automated system and should be reviewed by a qualified patent attorney before making filing decisions.*"
    )

    return "\n".join(lines)


def generate_brief_summary(ai_results: Dict[str, Any]) -> str:
    """
    Generate a one-paragraph brief summary for quick overview.

    Args:
        ai_results: The ai_detection_results dictionary

    Returns:
        str: Brief 2-3 sentence summary
    """
    if not ai_results or ai_results.get("status") == "ERROR":
        return "The analysis could not be completed. Please check your documents and try again."

    is_ai = ai_results.get("is_likely_ai_generated", False)
    confidence = ai_results.get("confidence_score", 0)
    risk_level = ai_results.get("risk_level", "UNKNOWN")
    enablement = ai_results.get("detailed_analysis", {}).get(
        "enablement_assessment", {}
    )
    enablement_conclusion = enablement.get("enablement_conclusion", "UNCLEAR")

    parts = []

    # AI conclusion
    if is_ai:
        if confidence >= 0.75:
            parts.append(
                f"⚠️ This patent document shows **strong indicators of AI generation** ({confidence:.1%} confidence, {risk_level} risk)."
            )
        else:
            parts.append(
                f"⚠️ This patent document **may be AI-generated** ({confidence:.1%} confidence, {risk_level} risk). The evidence is suggestive but not definitive."
            )
    else:
        if confidence <= 0.25:
            parts.append(
                f"✓ This patent document **appears to be human-written** ({(1 - confidence):.1%} confidence, {risk_level} risk)."
            )
        else:
            parts.append(
                f"✓ This patent document **is likely human-written** ({(1 - confidence):.1%} confidence, {risk_level} risk), though a few minor patterns were detected."
            )

    # Quality note
    if enablement_conclusion == "NOT_ENABLED":
        parts.append(
            "**Important:** The disclosure has a critical enablement issue — it lacks sufficient technical detail for legal validity. This needs immediate attention regardless of authorship."
        )
    elif enablement_conclusion == "ENABLED":
        parts.append("The technical disclosure appears solid and legally sufficient.")

    return " ".join(parts)
