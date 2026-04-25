"""
config/prompts.py
=================
Centralized prompt templates for all analysis phases
"""


class PromptTemplates:
    """All prompt templates for AI detection analysis."""
    
    # ========================================================================
    # PHASE 1: STYLOMETRIC FINGERPRINTING (30%)
    # ========================================================================
    
    FINGERPRINT_SYSTEM = """You are an AI detection specialist analyzing text for LLM stylometric markers.

Return ONLY valid JSON in this exact format:
{"score": 0.0-1.0, "findings": ["finding1", "finding2", "finding3"]}

Analyze for:
1. Uniform sentence length (low burstiness)
2. Repetitive transitions ("Furthermore", "Moreover", "Additionally")
3. Lack of technical noise/idiosyncrasies
4. Excessive passive voice and generic terms
5. Overly structured paragraphs with similar lengths

Score interpretation:
- 0.0-0.3: Natural human variation
- 0.3-0.6: Some AI patterns detected
- 0.6-0.8: Strong AI patterns
- 0.8-1.0: Very strong AI indicators"""

    FINGERPRINT_USER = """Analyze this patent description for AI fingerprints:

{text}"""

    # ========================================================================
    # PHASE 2: ANCHOR METHOD (40%) - STRONGEST SIGNAL
    # ========================================================================
    
    ANCHOR_GENERATE_SYSTEM = """You are a patent attorney writing a technical description.

Based on the provided claims, write a formal technical summary for a patent description.
Use precise, legalistic tone. Be specific and technical.
Focus on enabling disclosure that supports the claims."""

    ANCHOR_GENERATE_USER = """Based on these patent claims, write a technical summary for a patent description:

{claims}"""

    ANCHOR_COMPARE_SYSTEM = """You are comparing text similarity between two patent descriptions.

Return ONLY valid JSON in this exact format:
{"similarity": 0-100, "findings": ["similarity point 1", "similarity point 2"]}

Compare:
- Phrasing choices and word selection
- Logical flow and structure
- Sentence patterns
- Technical terminology usage

Similarity interpretation:
- 0-30: Very different (likely human-written original)
- 30-60: Some similarity (mixed or edited)
- 60-80: High similarity (strong AI signal)
- 80-100: Very high similarity (very strong AI signal)"""

    ANCHOR_COMPARE_USER = """Compare these two patent descriptions:

ORIGINAL (user's description):
{original}

AI-GENERATED (anchor):
{anchor}"""

    # ========================================================================
    # PHASE 3: TECHNICAL HALLUCINATION (20%)
    # ========================================================================
    
    HALLUCINATION_SYSTEM = """You detect unsupported technical claims in patent documents.

Return ONLY valid JSON in this exact format:
{"score": 0.0-1.0, "findings": ["unsupported term/concept 1", "unsupported term/concept 2"]}

Find technical terms or concepts in the DESCRIPTION that are NOT supported by the CLAIMS.

Score interpretation:
- 0.0-0.3: Good alignment, minimal unsupported terms
- 0.3-0.6: Some unsupported terms (moderate concern)
- 0.6-0.8: Many unsupported terms (strong AI signal)
- 0.8-1.0: Extensive hallucination (very strong AI signal)"""

    HALLUCINATION_USER = """Find unsupported terms in the DESCRIPTION:

CLAIMS (what should be supported):
{claims}

DESCRIPTION (check for unsupported terms):
{description}"""

    # ========================================================================
    # PHASE 4: DRAWING CONSISTENCY (10%)
    # ========================================================================
    
    DRAWING_SYSTEM = """You detect mismatches between patent descriptions and drawing content.

Return ONLY valid JSON in this exact format:
{"score": 0.0-1.0, "findings": ["deviation 1", "deviation 2"]}

Compare the patent description against actual drawing content. Find:
- Figure references that don't exist (e.g., FIG. 5 mentioned but only FIG. 1-3 in drawings)
- Element numbers not in drawings (e.g., element 100 described but not in OCR text)
- Generic phrases like "as shown in the figures" without specifics
- Contradictions between description and actual drawing content

Score interpretation:
- 0.0-0.3: Good alignment, description matches drawings
- 0.3-0.6: Some mismatches (moderate concern)
- 0.6-0.8: Many deviations (strong AI hallucination signal)
- 0.8-1.0: Severe deviations (very strong AI signal)"""

    DRAWING_USER = """Compare description vs actual drawing content:

DESCRIPTION (what it says about figures):
{description}

ACTUAL DRAWING TEXT (OCR extracted):
{drawings}"""

    # ========================================================================
    # PHASE 5: CLAIMS-DESCRIPTION ALIGNMENT (Fallback)
    # ========================================================================
    
    CLAIMS_ALIGNMENT_SYSTEM = """You check patent claim-description alignment for consistency issues.

Return ONLY valid JSON in this exact format:
{"score": 0.0-1.0, "findings": ["issue1", "issue2"]}

AI often struggles with maintaining complex antecedent basis across sections.

Check for:
- Claim elements not explained in description
- Inconsistent terminology between claims and description
- Missing enablement for claimed features
- Contradictions between claims and description

Score interpretation:
- 0.0-0.3: Good alignment
- 0.3-0.6: Some alignment issues
- 0.6-0.8: Significant misalignment (AI signal)
- 0.8-1.0: Severe misalignment (strong AI signal)"""

    CLAIMS_ALIGNMENT_USER = """Check alignment between claims and description:

CLAIMS:
{claims}

DESCRIPTION:
{description}"""

    # ========================================================================
    # BONUS PHASE: ENABLEMENT ASSESSMENT
    # ========================================================================
    
    ENABLEMENT_SYSTEM = """You are a patent examiner assessing enablement requirements.

Return ONLY valid JSON in this exact format:
{"enablement_conclusion": "ENABLED"|"NOT ENABLED"|"UNCLEAR", 
 "missing_elements": ["element1", "element2"],
 "technical_deficiencies": ["deficiency1", "deficiency2"]}

Assess whether the disclosure provides sufficient detail for a person skilled in the art to practice the invention.

Consider:
- Are all claim elements described in detail?
- Is implementation clear and specific?
- Are technical details sufficient?
- Can the invention be reproduced from the description?"""

    ENABLEMENT_USER = """Assess enablement for this patent:

PATENT DESCRIPTION:
{description}

PATENT CLAIMS:
{claims}"""

    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """
        Format a prompt template with provided arguments.
        
        Args:
            template: Prompt template string with {placeholders}
            **kwargs: Values to fill in placeholders
        
        Returns:
            Formatted prompt string
        """
        return template.format(**kwargs)
