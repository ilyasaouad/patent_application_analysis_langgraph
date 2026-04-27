"""
antecedent_NLP_analyzer.py
==========================
Core antecedent basis analysis using spaCy NLP.

Performs intra-claim and cross-claim antecedent validation.
Uses spaCy for primary detection, with optional LLM fallback.
"""

import re
from typing import List, Set, Dict, Any, Tuple, Optional
from dataclasses import dataclass

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("WARNING: spaCy not installed. Install with: pip install spacy")
    print("   Then download model: python -m spacy download en_core_web_sm")


@dataclass
class Claim:
    """Represents a single patent claim."""

    number: int
    text: str
    dependencies: List[int]  # Claim numbers this claim depends on


@dataclass
class AntecedentIssue:
    """Represents a missing antecedent issue."""

    claim_number: int
    term: str
    definite_reference: str
    context: str
    confidence: str  # "high", "medium", "low"
    reasoning: str


class AntecedentAnalyzer:
    """
    Analyzes patent claims for antecedent basis issues using spaCy NLP.

    Features:
    - Intra-claim analysis (same claim)
    - Cross-claim analysis (ancestor claims)
    - Singular/plural matching
    - spaCy NLP for enhanced detection
    """

    # Definite references requiring antecedent
    DEFINITE_PATTERNS = [
        r"\b(the|said|this|that)\s+([a-zA-Z][a-zA-Z0-9\-_\s]{2,100})\b",
    ]

    # Indefinite introductions (antecedents)
    INDEFINITE_PATTERNS = [
        r"\b(a|an)\s+([a-zA-Z][a-zA-Z0-9\-_\s]{2,100})\b",
        r"\b(one\s+or\s+more\s+[a-zA-Z]+|plurality\s+of\s+[a-zA-Z]+)\b",
    ]

    # Terms to ignore (generic patent terms)
    IGNORE_TERMS = {
        "method",
        "apparatus",
        "system",
        "device",
        "invention",
        "embodiment",
        "example",
        "claim",
        "figure",
        "fig",
        "step",
        "process",
        "apparatus",
        "composition",
    }

    def __init__(self, use_spacy: bool = True):
        """
        Initialize analyzer.

        Args:
            use_spacy: Whether to use spaCy NLP (if available)
        """
        self.nlp = None
        self.use_spacy = use_spacy and SPACY_AVAILABLE

        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✓ spaCy model loaded successfully")
            except OSError:
                print(
                    "⚠️ spaCy model not found. Install with: python -m spacy download en_core_web_sm"
                )
                self.use_spacy = False

    def _normalize_term(self, term: str) -> str:
        """
        Normalize term for comparison.
        - Lowercase
        - Strip whitespace
        - Remove extra spaces
        - Simple plural handling
        """
        term = term.lower().strip()
        term = re.sub(r"\s+", " ", term)

        # Simple stemming: remove trailing 's' if present
        # More sophisticated stemming could use NLTK or spaCy
        if term.endswith("s") and len(term) > 3:
            term = term[:-1]

        return term

    def _extract_definite_references(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract definite references from text.

        Returns:
            List of (determiner, noun_phrase) tuples
            e.g., [("the", "actuator"), ("said", "housing")]
        """
        references = []

        for pattern in self.DEFINITE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                determiner = match.group(1).lower()
                noun_phrase = match.group(2).strip()

                # Skip ignored terms
                normalized = self._normalize_term(noun_phrase)
                if normalized in self.IGNORE_TERMS:
                    continue

                references.append((determiner, noun_phrase))

        # spaCy enhancement
        if self.use_spacy and self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.lower_ in ("the", "said", "this", "that"):
                    # Get the noun phrase
                    if token.head.pos_ in ("NOUN", "PROPN"):
                        np_text = self._get_noun_phrase(token.head)
                        if (
                            np_text
                            and self._normalize_term(np_text) not in self.IGNORE_TERMS
                        ):
                            references.append((token.lower_, np_text))

        # Remove duplicates while preserving order
        seen = set()
        unique_refs = []
        for det, np in references:
            key = (det.lower(), self._normalize_term(np))
            if key not in seen:
                seen.add(key)
                unique_refs.append((det, np))

        return unique_refs

    def _get_noun_phrase(self, token) -> str:
        """Extract full noun phrase from spaCy token."""
        # Get compound nouns and modifiers
        parts = []

        # Check for compound modifiers before the noun
        for child in token.children:
            if child.dep_ in ("compound", "amod", "nummod"):
                parts.append(child.text)

        parts.append(token.text)
        return " ".join(parts)

    def _extract_antecedents(self, text: str) -> Set[str]:
        """
        Extract antecedent introductions from text.

        Returns:
            Set of normalized terms that have been introduced
        """
        antecedents = set()

        # Pattern-based extraction
        for pattern in self.INDEFINITE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.lastindex >= 2:
                    noun_phrase = match.group(2).strip()
                else:
                    noun_phrase = match.group(0).strip()

                normalized = self._normalize_term(noun_phrase)
                if normalized and normalized not in self.IGNORE_TERMS:
                    antecedents.add(normalized)

        # spaCy enhancement: look for direct objects, subjects
        if self.use_spacy and self.nlp:
            doc = self.nlp(text)
            for token in doc:
                # Look for nouns that are objects of "comprising", "having", etc.
                if token.pos_ in ("NOUN", "PROPN"):
                    # Check if preceded by "a" or "an"
                    if token.i > 0:
                        prev_token = doc[token.i - 1]
                        if prev_token.lower_ in ("a", "an"):
                            np_text = self._get_noun_phrase(token)
                            normalized = self._normalize_term(np_text)
                            if normalized not in self.IGNORE_TERMS:
                                antecedents.add(normalized)

        return antecedents

    def _find_ancestor_claims(
        self, claim: Claim, all_claims: List[Claim]
    ) -> List[Claim]:
        """
        Find all ancestor claims that a claim depends on.

        Args:
            claim: The claim to analyze
            all_claims: List of all claims

        Returns:
            List of ancestor claims in order (closest first)
        """
        ancestors = []
        claim_map = {c.number: c for c in all_claims}

        # Direct dependencies
        for dep_num in claim.dependencies:
            if dep_num in claim_map:
                ancestors.append(claim_map[dep_num])

        # Recursive dependencies
        for dep_num in list(claim.dependencies):
            if dep_num in claim_map:
                ancestor = claim_map[dep_num]
                # Get ancestors of this ancestor
                for anc in self._find_ancestor_claims(ancestor, all_claims):
                    if anc not in ancestors:
                        ancestors.append(anc)

        # Sort by claim number
        ancestors.sort(key=lambda c: c.number)
        return ancestors

    def _check_term_in_antecedents(self, term: str, antecedents: Set[str]) -> bool:
        """
        Check if a term has a matching antecedent.

        Handles:
        - Exact match
        - Singular/plural variants
        - Substring match (e.g., "top plate" matches "plate")
        """
        normalized_term = self._normalize_term(term)

        for antecedent in antecedents:
            normalized_antecedent = self._normalize_term(antecedent)

            # Exact match
            if normalized_term == normalized_antecedent:
                return True

            # Substring match: "top plate" should match "plate"
            if (
                normalized_term in normalized_antecedent
                or normalized_antecedent in normalized_term
            ):
                # Avoid false positives: "plate" shouldn't match "platen"
                if len(normalized_term) >= 4 and len(normalized_antecedent) >= 4:
                    return True

        return False

    def analyze_claim(
        self, claim: Claim, all_claims: List[Claim]
    ) -> List[AntecedentIssue]:
        """
        Analyze a single claim for antecedent basis issues.

        Args:
            claim: The claim to analyze
            all_claims: List of all claims for cross-claim analysis

        Returns:
            List of antecedent issues found
        """
        issues = []

        # Extract definite references in this claim
        definite_refs = self._extract_definite_references(claim.text)

        # Extract antecedents from this claim (intra-claim)
        # Only look at text before each reference
        intra_antecedents = self._extract_antecedents(claim.text)

        # Get ancestor claims
        ancestor_claims = self._find_ancestor_claims(claim, all_claims)

        # Extract antecedents from ancestor claims
        ancestor_antecedents = set()
        for ancestor in ancestor_claims:
            ancestor_antecedents.update(self._extract_antecedents(ancestor.text))

        # Check each definite reference
        for determiner, noun_phrase in definite_refs:
            # Check intra-claim first
            if self._check_term_in_antecedents(noun_phrase, intra_antecedents):
                continue

            # Check ancestor claims
            if self._check_term_in_antecedents(noun_phrase, ancestor_antecedents):
                continue

            # No antecedent found - flag as issue
            issue = AntecedentIssue(
                claim_number=claim.number,
                term=noun_phrase,
                definite_reference=f"{determiner} {noun_phrase}",
                context=self._get_context(claim.text, noun_phrase),
                confidence="high",
                reasoning=f"No antecedent found for '{determiner} {noun_phrase}' in claim {claim.number} or ancestor claims",
            )
            issues.append(issue)

        return issues

    def _get_context(self, text: str, term: str, window: int = 50) -> str:
        """Get context around a term in text."""
        idx = text.lower().find(term.lower())
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(term) + window)
        return text[start:end]

    def analyze_all_claims(self, claims_text: str) -> Dict[str, Any]:
        """
        Analyze all claims for antecedent basis issues.

        Args:
            claims_text: Full claims text

        Returns:
            Dictionary with analysis results
        """
        # Parse claims
        claims = self._parse_claims(claims_text)

        if not claims:
            return {
                "status": "ERROR",
                "error": "No claims could be parsed",
                "issues": [],
                "claim_count": 0,
            }

        all_issues = []

        for claim in claims:
            issues = self.analyze_claim(claim, claims)
            all_issues.extend(issues)

        # Calculate statistics
        claims_with_issues = len(set(issue.claim_number for issue in all_issues))

        return {
            "status": "SUCCESS",
            "claim_count": len(claims),
            "issues_found": len(all_issues),
            "claims_with_issues": claims_with_issues,
            "issues": [
                {
                    "claim_number": issue.claim_number,
                    "term": issue.term,
                    "definite_reference": issue.definite_reference,
                    "context": issue.context,
                    "confidence": issue.confidence,
                    "reasoning": issue.reasoning,
                }
                for issue in all_issues
            ],
        }

    def _parse_claims(self, text: str) -> List[Claim]:
        """
        Parse claims text into Claim objects.

        Handles:
        - "1. A system..."
        - "Claim 1: A system..."
        - Numbered lists
        """
        claims = []

        # Try to find claim numbers and text
        # Pattern: number followed by period or parenthesis
        lines = text.split("\n")
        current_claim = None
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line starts a new claim
            match = re.match(r"^(?:claim\s*)?(\d+)[\.\)]\s*(.*)", line, re.IGNORECASE)
            if match:
                # Save previous claim
                if current_claim is not None:
                    claims.append(
                        Claim(
                            number=current_claim,
                            text=" ".join(current_text),
                            dependencies=self._extract_dependencies(
                                " ".join(current_text)
                            ),
                        )
                    )

                current_claim = int(match.group(1))
                current_text = [match.group(2)]
            else:
                if current_claim is not None:
                    current_text.append(line)

        # Save last claim
        if current_claim is not None:
            claims.append(
                Claim(
                    number=current_claim,
                    text=" ".join(current_text),
                    dependencies=self._extract_dependencies(" ".join(current_text)),
                )
            )

        return claims

    def _extract_dependencies(self, text: str) -> List[int]:
        """
        Extract claim dependencies from text.

        Looks for phrases like:
        - "according to claim 1"
        - "as claimed in claim 1"
        - "of claim 1"
        """
        deps = []

        patterns = [
            r"according\s+to\s+claim\s+(\d+)",
            r"as\s+claimed\s+in\s+claim\s+(\d+)",
            r"of\s+claim\s+(\d+)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                deps.append(int(match.group(1)))

        return deps

    def get_ambiguous_terms(self, claim: Claim) -> List[str]:
        """
        Identify terms that might be ambiguous and need LLM validation.

        Returns:
            List of potentially ambiguous terms
        """
        ambiguous = []
        definite_refs = self._extract_definite_references(claim.text)

        for determiner, noun_phrase in definite_refs:
            # Complex noun phrases (multiple words) are more ambiguous
            if len(noun_phrase.split()) > 2:
                ambiguous.append(f"{determiner} {noun_phrase}")

        return ambiguous
