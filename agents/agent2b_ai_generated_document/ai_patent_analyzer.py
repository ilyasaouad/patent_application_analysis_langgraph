"""
ai_patent_analyzer.py
=====================
Main AI Detection Analyzer for Patent Documents
Refactored modular architecture with separated concerns
"""

import os
import glob
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from .config import AnalyzerConfig, PromptTemplates
from .core import OllamaClient, DetectionResult, PatentDocument
from .utils import truncate_text, parse_json_safe, remove_margin_numbers


class AIPatentAnalyzer:
    """
    AI Detection Analyzer for Patent Documents.

    Features:
    - Multi-phase weighted analysis (30%/40%/20%/10%)
    - Patent-specific checks (enablement, claims alignment)
    - 100% LOCAL (Ollama) - Privacy-focused
    - Modular architecture with clean separation
    """

    def __init__(
        self, input_dir: Optional[str] = None, config: Optional[AnalyzerConfig] = None
    ):
        """
        Initialize the analyzer.

        Args:
            input_dir: Directory containing patent markdown files
            config: Configuration object (uses defaults if None)
        """
        self.config = config or AnalyzerConfig()
        self.input_dir = input_dir

        # Validate configuration
        if not self.config.validate():
            print("⚠️ Configuration validation failed, using defaults anyway")

        # Initialize LLM client
        self.client = OllamaClient(
            model_name=self.config.OLLAMA_MODEL, base_url=self.config.OLLAMA_URL
        )

        # Document storage
        self.documents: List[PatentDocument] = []
        self.description_text: str = ""
        self.claims_text: str = ""
        self.drawings_text: str = ""

        # Test connection
        self._test_connection()

        # Load documents if directory provided
        if input_dir:
            self._load_documents()

    def _test_connection(self) -> None:
        """Test Ollama connection and provide actionable feedback."""
        print(f"🔌 Testing connection to Ollama...")

        if self.client.test_connection():
            print(f"✓ Connected to Ollama at {self.config.OLLAMA_URL}")
            print(f"✓ Model: {self.config.OLLAMA_MODEL}")
        else:
            print(f"❌ Cannot connect to Ollama")
            print("\n💡 Troubleshooting:")
            print("   1. Start Ollama: ollama serve")
            print(f"   2. Pull model: ollama pull {self.config.OLLAMA_MODEL}")
            print("   3. Check models: ollama list")
            print("   4. Test: curl http://localhost:11434/api/tags")

            available = self.client.get_available_models()
            if available:
                print(f"\n📋 Available models: {', '.join(available[:5])}")

            raise ConnectionError(f"Ollama connection failed")

    def _load_documents(self) -> None:
        """Load and categorize markdown files from input directory."""
        if not os.path.isdir(self.input_dir):
            print(f"⚠️ Directory '{self.input_dir}' does not exist.")
            return

        # Find all markdown files
        search_pattern = os.path.join(self.input_dir, "*.md")
        md_files = glob.glob(search_pattern)

        for file_path in md_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Clean the pesky OCR margin numbers!
                    content = remove_margin_numbers(content)

                    file_name = os.path.basename(file_path).lower()

                    # Determine document type
                    doc_type = self._determine_doc_type(file_name)

                    # Store document object
                    doc = PatentDocument(
                        file_name=os.path.basename(file_path),
                        file_path=file_path,
                        content=content,
                        doc_type=doc_type,
                    )

                    if doc.is_empty():
                        print(f"⚠️ Skipping empty document: {doc.file_name}")
                        continue

                    self.documents.append(doc)

                    # Store in appropriate variable
                    if doc_type == "claims":
                        self.claims_text = content
                        print(
                            f"✓ Loaded claims: {doc.file_name} ({doc.get_word_count()} words)"
                        )
                    elif doc_type == "description":
                        self.description_text = content
                        print(
                            f"✓ Loaded description: {doc.file_name} ({doc.get_word_count()} words)"
                        )
                    elif doc_type == "drawings":
                        self.drawings_text = content
                        print(
                            f"✓ Loaded drawings: {doc.file_name} ({doc.get_word_count()} words)"
                        )
                    else:
                        print(
                            f"✓ Loaded: {doc.file_name} ({doc.get_word_count()} words)"
                        )

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")

        print(f"\n📄 Loaded {len(self.documents)} document(s)")
        print(f"   Description: {'✓' if self.description_text else '✗'}")
        print(f"   Claims: {'✓' if self.claims_text else '✗'}")
        print(f"   Drawings: {'✓' if self.drawings_text else '✗'}")

    def _determine_doc_type(self, file_name: str) -> str:
        """
        Determine document type from filename.

        Args:
            file_name: Lowercase filename

        Returns:
            str: "claims", "description", "drawings", or "unknown"
        """
        # Check patterns from config
        if any(pattern in file_name for pattern in self.config.CLAIMS_PATTERNS):
            return "claims"
        elif any(pattern in file_name for pattern in self.config.DESCRIPTION_PATTERNS):
            return "description"
        elif any(pattern in file_name for pattern in self.config.DRAWING_PATTERNS):
            return "drawings"
        else:
            return "unknown"

    # ========================================================================
    # ANALYSIS PHASES
    # ========================================================================

    def _phase_fingerprint(self) -> Dict[str, Any]:
        """Phase 1: Stylometric Fingerprinting (30% weight)."""
        if not self.description_text:
            return {"score": 0.5, "findings": ["No description text available"]}

        print("  Step 1/6: Stylometric fingerprinting...")

        prompt = PromptTemplates.format_prompt(
            PromptTemplates.FINGERPRINT_USER,
            text=truncate_text(self.description_text, self.config.MAX_INPUT_CHARS),
        )

        response = self.client.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.FINGERPRINT_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        return parse_json_safe(
            response, {"score": 0.5, "findings": ["Analysis incomplete"]}
        )

    def _phase_anchor(self) -> Dict[str, Any]:
        """Phase 2: Anchor Method - Self-Reflexive Comparison (40% weight)."""
        if not self.claims_text or not self.description_text:
            return {
                "similarity": 0.5,
                "findings": ["Insufficient text for anchor method"],
            }

        print("  Step 2/6: Anchor method (self-reflexive comparison)...")

        # Generate AI anchor from claims
        print("     → Generating AI anchor from claims...")
        gen_prompt = PromptTemplates.format_prompt(
            PromptTemplates.ANCHOR_GENERATE_USER,
            claims=truncate_text(self.claims_text, 2000),
        )

        ai_anchor = self.client.generate(
            prompt=gen_prompt,
            system_prompt=PromptTemplates.ANCHOR_GENERATE_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        if not ai_anchor or len(ai_anchor) < 50:
            return {"similarity": 0.5, "findings": ["Anchor generation failed"]}

        # Compare original with AI-generated anchor
        print("     → Comparing original with AI-generated anchor...")
        compare_prompt = PromptTemplates.format_prompt(
            PromptTemplates.ANCHOR_COMPARE_USER,
            original=truncate_text(self.description_text, 2000),
            anchor=truncate_text(ai_anchor, 2000),
        )

        response = self.client.generate(
            prompt=compare_prompt,
            system_prompt=PromptTemplates.ANCHOR_COMPARE_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        result = parse_json_safe(
            response, {"similarity": 50, "findings": ["Comparison incomplete"]}
        )

        # Normalize similarity to 0-1 range
        if "similarity" in result:
            result["similarity"] = result["similarity"] / 100.0

        return result

    def _phase_hallucination(self) -> Dict[str, Any]:
        """Phase 3: Technical Hallucination Detection (20% weight)."""
        if not self.claims_text or not self.description_text:
            return {"score": 0.5, "findings": ["Insufficient text"]}

        print("  Step 3/6: Checking for technical hallucinations...")

        prompt = PromptTemplates.format_prompt(
            PromptTemplates.HALLUCINATION_USER,
            claims=truncate_text(self.claims_text, 2000),
            description=truncate_text(self.description_text, 3000),
        )

        response = self.client.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.HALLUCINATION_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        return parse_json_safe(
            response, {"score": 0.5, "findings": ["Analysis incomplete"]}
        )

    def _phase_drawing(self) -> Dict[str, Any]:
        """Phase 4: Drawing Consistency (10% weight)."""
        print("  Step 4/6: Analyzing drawing consistency...")

        if not self.drawings_text:
            # Check if drawings are referenced in description
            drawing_patterns = r"(?i)(brief description of the drawings?|accompanying drawings?|referring to figure|shown in fig|figur\s+\d+|fig\.\s*\d+)"

            if self.description_text and re.search(
                drawing_patterns, self.description_text
            ):
                return {
                    "score": 0.7,
                    "findings": [
                        "WARNING: Description references drawings but no drawing file provided"
                    ],
                }
            else:
                # Fallback to claims-description alignment
                return self._phase_claims_alignment()

        prompt = PromptTemplates.format_prompt(
            PromptTemplates.DRAWING_USER,
            description=truncate_text(self.description_text, 3000),
            drawings=truncate_text(self.drawings_text, 1500),
        )

        response = self.client.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.DRAWING_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        return parse_json_safe(
            response, {"score": 0.5, "findings": ["Analysis incomplete"]}
        )

    def _phase_claims_alignment(self) -> Dict[str, Any]:
        """Fallback: Check claims-description alignment."""
        if not self.claims_text or not self.description_text:
            return {"score": 0.5, "findings": ["Insufficient text"]}

        system_prompt = """You check patent claim-description alignment for consistency issues.
Return ONLY valid JSON: {"score": 0.0-1.0, "findings": ["issue1", "issue2"]}

AI often struggles with maintaining complex antecedent basis across sections."""

        prompt = f"""CLAIMS:
{truncate_text(self.claims_text, 2000)}

DESCRIPTION:
{truncate_text(self.description_text, 3000)}"""

        response = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        return parse_json_safe(
            response, {"score": 0.5, "findings": ["Analysis incomplete"]}
        )

    def _phase_enablement(self) -> Dict[str, Any]:
        """Phase 5: Patent Enablement Assessment (bonus check)."""
        if not self.claims_text or not self.description_text:
            return {
                "enablement_conclusion": "UNCLEAR",
                "missing_elements": [],
                "technical_deficiencies": [],
            }

        print("  Step 5/6: Assessing patent enablement...")

        prompt = PromptTemplates.format_prompt(
            PromptTemplates.ENABLEMENT_USER,
            description=truncate_text(self.description_text, 3000),
            claims=truncate_text(self.claims_text, 2000),
        )

        response = self.client.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.ENABLEMENT_SYSTEM,
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
        )

        return parse_json_safe(
            response,
            {
                "enablement_conclusion": "UNCLEAR",
                "missing_elements": [],
                "technical_deficiencies": [],
            },
        )

    # ========================================================================
    # CALCULATION & OUTPUT
    # ========================================================================

    def _calculate_confidence(
        self, fingerprint: Dict, anchor: Dict, hallucination: Dict, drawing: Dict
    ) -> float:
        """Calculate weighted confidence score from all phases."""
        fp_score = fingerprint.get("score", 0.5) * self.config.WEIGHT_FINGERPRINT
        anchor_score = anchor.get("similarity", 0.5) * self.config.WEIGHT_ANCHOR
        hall_score = hallucination.get("score", 0.5) * self.config.WEIGHT_HALLUCINATION
        draw_score = drawing.get("score", 0.5) * self.config.WEIGHT_DRAWING

        total = fp_score + anchor_score + hall_score + draw_score
        return max(0.0, min(1.0, total))

    def _get_risk_level(self, confidence: float) -> str:
        """Determine risk level from confidence score."""
        if confidence >= self.config.HIGH_RISK_THRESHOLD:
            return "HIGH"
        elif confidence >= self.config.MEDIUM_RISK_THRESHOLD:
            return "MEDIUM"
        elif confidence >= self.config.LOW_RISK_THRESHOLD:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendations(
        self, confidence: float, fingerprint: Dict, anchor: Dict, enablement: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        # Critical: Anchor similarity (strongest signal)
        anchor_sim = anchor.get("similarity", 0.5)
        if anchor_sim > 0.75:
            recs.append("🚨 CRITICAL: High anchor similarity (>75%) - strong AI signal")
            recs.append("   AI generated very similar text when given same claims")
            recs.append("   Action: Manual review required before filing")

        # Confidence-based recommendations
        if confidence >= self.config.HIGH_RISK_THRESHOLD:
            recs.append("⚠️ HIGH RISK: Strong AI indicators detected")
            recs.append("   Action: Perform thorough manual review")
        elif confidence >= self.config.MEDIUM_RISK_THRESHOLD:
            recs.append("⚠️ MEDIUM RISK: Moderate AI indicators detected")
            recs.append("   Action: Spot-check sections with repetitive patterns")
        elif confidence >= self.config.LOW_RISK_THRESHOLD:
            recs.append("✓ LOW RISK: Minimal AI indicators")
        else:
            recs.append("✓ MINIMAL RISK: No significant AI signals detected")

        # Enablement-specific recommendations
        if enablement.get("enablement_conclusion") == "NOT ENABLED":
            recs.append("\n⚖️ ENABLEMENT ISSUE:")
            recs.append("   CRITICAL: Patent disclosure lacks enablement")
            recs.append("   Action: Request additional technical details")

        # Add specific findings
        for finding in fingerprint.get("findings", [])[:2]:
            recs.append(f"• {finding}")

        return recs

    def run_analysis(self) -> DetectionResult:
        """
        Run complete multi-phase analysis on loaded documents.

        Returns:
            DetectionResult: Typed, system-compatible result object
        """
        print(f"\n{'=' * 70}")
        print(f"🔍 AI PATENT ANALYSIS - LOCAL MODE (Ollama)")
        print(f"{'=' * 70}")
        print(f" Model: {self.config.OLLAMA_MODEL}")
        print(f" Files: {len(self.documents)}")
        print(f"{'=' * 70}\n")

        if not self.documents:
            return DetectionResult(
                is_likely_ai_generated=False,
                confidence_score=0.0,
                risk_level="ERROR",
                feature_scores={},
                detailed_analysis={"error": "No documents"},
                recommendations=["Provide documents"],
                applied_rules=[],
            )

        # Run all phases
        fingerprint = self._phase_fingerprint()
        anchor = self._phase_anchor()
        hallucination = self._phase_hallucination()
        drawing = self._phase_drawing()
        enablement = self._phase_enablement()

        print("  Step 6/6: Calculating final confidence...")

        # Calculate confidence
        confidence = self._calculate_confidence(
            fingerprint, anchor, hallucination, drawing
        )

        # Build result
        result = DetectionResult(
            is_likely_ai_generated=confidence >= self.config.AI_DETECTION_THRESHOLD,
            confidence_score=round(confidence, 3),
            risk_level=self._get_risk_level(confidence),
            feature_scores={
                "fingerprint": fingerprint.get("score", 0.5),
                "anchor_similarity": anchor.get("similarity", 0.5),
                "hallucination": hallucination.get("score", 0.5),
                "drawing": drawing.get("score", 0.5),
            },
            detailed_analysis={
                "fingerprint_analysis": fingerprint,
                "anchor_analysis": anchor,
                "hallucination_analysis": hallucination,
                "drawing_analysis": drawing,
                "enablement_assessment": enablement,
                "model_used": self.config.OLLAMA_MODEL,
            },
            recommendations=self._generate_recommendations(
                confidence, fingerprint, anchor, enablement
            ),
            applied_rules=[],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "threshold": self.config.AI_DETECTION_THRESHOLD,
                    "weights": {
                        "fingerprint": self.config.WEIGHT_FINGERPRINT,
                        "anchor": self.config.WEIGHT_ANCHOR,
                        "hallucination": self.config.WEIGHT_HALLUCINATION,
                        "drawing": self.config.WEIGHT_DRAWING,
                    },
                },
            },
        )

        self._print_summary(result)

        # Save results
        agent_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(agent_dir, "ai_detection_result.json")
        result.save_json(output_path)

        return result

    def _print_summary(self, result: DetectionResult) -> None:
        """Print summary."""
        print(f"\n{'=' * 70}")
        print("📊 AI DETECTION RESULT")
        print(f"{'=' * 70}")
        print(result.get_summary())
        print(f"{'=' * 70}")

        scores = result.feature_scores
        print("\n📈 Detailed Scores:")
        print(f"  Fingerprint: {scores.get('fingerprint', 0):.1%} (30%)")
        print(f"  Anchor: {scores.get('anchor_similarity', 0):.1%} (40%) 👈 Strongest")
        print(f"  Hallucination: {scores.get('hallucination', 0):.1%} (20%)")
        print(f"  Drawing: {scores.get('drawing', 0):.1%} (10%)")

        # Enablement
        enablement = result.detailed_analysis.get("enablement_assessment", {})
        if enablement:
            print(
                f"\n⚖️ Enablement: {enablement.get('enablement_conclusion', 'UNKNOWN')}"
            )

        print("\n📋 Recommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")

        print(f"\n{'=' * 70}\n")

    def analyze_text(
        self, text: str, claims: Optional[str] = None, drawings: Optional[str] = None
    ) -> DetectionResult:
        """
        Analyze raw text without loading from directory.

        Args:
            text: Patent description text
            claims: Optional claims text
            drawings: Optional drawings text

        Returns:
            DetectionResult: Analysis result
        """
        self.description_text = text
        self.claims_text = claims or ""
        self.drawings_text = drawings or ""

        self.documents = [
            PatentDocument(
                file_name="direct_input.txt",
                file_path="memory",
                content=text,
                doc_type="description",
            )
        ]

        return self.run_analysis()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    document_dir = os.path.join(parent_dir, "document_text_output")

    print("=" * 70)
    print("🤖 AI PATENT DETECTION ANALYZER")
    print("=" * 70)
    print("✓ Multi-phase weighted analysis")
    print("✓ LOCAL (Ollama) - 100% privacy")
    print("✓ Patent enablement assessment")
    print("=" * 70)

    try:
        config_path = os.path.join(current_dir, "analyzer_config.json")
        config = AnalyzerConfig.from_settings_file(config_path)

        analyzer = AIPatentAnalyzer(input_dir=document_dir, config=config)
        result = analyzer.run_analysis()

        print(
            f"\n✅ Complete! AI: {result.is_likely_ai_generated} ({result.confidence_score:.1%})"
        )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
