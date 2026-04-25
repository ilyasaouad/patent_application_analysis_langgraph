"""
core/models.py
==============
Data models for AI Patent Analyzer

This module defines the core data structures used throughout the analyzer:
- DetectionResult: The output of the analysis
- PatentDocument: Represents a loaded patent file

These models provide type safety, JSON serialization, and clear contracts
for integration with other systems.
"""

import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class DetectionResult:
    """
    Structured detection result for system integration.
    Compatible with existing patent analysis systems.
    
    This is the primary output of the AI detection analyzer.
    Contains all scores, findings, and recommendations.
    
    Attributes:
        is_likely_ai_generated: Boolean flag indicating AI detection
        confidence_score: Float 0.0-1.0 representing detection confidence
        risk_level: String "HIGH", "MEDIUM", "LOW", "MINIMAL", or "ERROR"
        feature_scores: Dict of individual phase scores
        detailed_analysis: Full analysis results from each phase
        recommendations: List of actionable recommendations
        applied_rules: List of detection rules that were applied
        metadata: Optional metadata (timestamp, version, config)
    
    Example:
        >>> result = DetectionResult(
        ...     is_likely_ai_generated=True,
        ...     confidence_score=0.732,
        ...     risk_level="MEDIUM",
        ...     feature_scores={
        ...         "fingerprint": 0.68,
        ...         "anchor_similarity": 0.85,
        ...         "hallucination": 0.65,
        ...         "drawing": 0.58
        ...     },
        ...     detailed_analysis={...},
        ...     recommendations=["Review manually"],
        ...     applied_rules=["anchor_method", "fingerprint"]
        ... )
        >>> print(result)
        DetectionResult(
          AI Generated: True
          Confidence: 73.2%
          Risk Level: MEDIUM
        )
    """
    
    is_likely_ai_generated: bool
    confidence_score: float
    risk_level: str  # "HIGH", "MEDIUM", "LOW", "MINIMAL", "ERROR"
    feature_scores: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    recommendations: List[str]
    applied_rules: List[str]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """
        Initialize metadata if not provided.
        Automatically adds timestamp and version on creation.
        """
        if self.metadata is None:
            self.metadata = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "analyzer": "ai_patent_analyzer"
            }
        
        # Validate confidence score range
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"confidence_score must be 0.0-1.0, got {self.confidence_score}")
        
        # Validate risk level
        valid_levels = {"HIGH", "MEDIUM", "LOW", "MINIMAL", "ERROR"}
        if self.risk_level not in valid_levels:
            raise ValueError(f"risk_level must be one of {valid_levels}, got {self.risk_level}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            dict: Complete result as dictionary with all fields
        
        Example:
            >>> result.to_dict()
            {
                'is_likely_ai_generated': True,
                'confidence_score': 0.732,
                'risk_level': 'MEDIUM',
                'feature_scores': {...},
                'detailed_analysis': {...},
                'recommendations': [...],
                'applied_rules': [...],
                'metadata': {...}
            }
        """
        return asdict(self)
    
    def save_json(self, output_path: str) -> None:
        """
        Save result to JSON file.
        
        Args:
            output_path: Path to output JSON file
        
        Raises:
            IOError: If file cannot be written
        
        Example:
            >>> result.save_json("ai_detection_result.json")
            ✓ Results saved to: ai_detection_result.json
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Results saved to: {output_path}")
        except Exception as e:
            print(f"✗ Error saving results: {e}")
            raise
    
    def __str__(self) -> str:
        """
        Human-readable string representation.
        
        Returns:
            str: Formatted string with key results
        
        Example:
            >>> print(result)
            DetectionResult(
              AI Generated: True
              Confidence: 73.2%
              Risk Level: MEDIUM
            )
        """
        return (
            f"DetectionResult(\n"
            f"  AI Generated: {self.is_likely_ai_generated}\n"
            f"  Confidence: {self.confidence_score:.1%}\n"
            f"  Risk Level: {self.risk_level}\n"
            f")"
        )
    
    def get_summary(self) -> str:
        """
        Get one-line summary of result.
        
        Returns:
            str: Compact summary
        
        Example:
            >>> result.get_summary()
            'AI: Yes (73.2% confidence) - MEDIUM risk'
        """
        ai_status = "Yes" if self.is_likely_ai_generated else "No"
        return f"AI: {ai_status} ({self.confidence_score:.1%} confidence) - {self.risk_level} risk"
    
    def is_high_risk(self) -> bool:
        """Check if result is high risk."""
        return self.risk_level == "HIGH"
    
    def is_conclusive(self) -> bool:
        """Check if result is conclusive (not ERROR or unclear)."""
        return self.risk_level != "ERROR" and self.confidence_score > 0.0


@dataclass
class PatentDocument:
    """
    Represents a loaded patent document.
    
    Used to store individual files (description, claims, drawings)
    loaded from the input directory.
    
    Attributes:
        file_name: Name of the file (e.g., "description.md")
        file_path: Full path to the file
        content: Text content of the file
        doc_type: Type of document ("description", "claims", "drawings", "unknown")
    
    Example:
        >>> doc = PatentDocument(
        ...     file_name="description.md",
        ...     file_path="/path/to/description.md",
        ...     content="A system comprising...",
        ...     doc_type="description"
        ... )
        >>> len(doc)
        24
        >>> doc.is_empty()
        False
    """
    
    file_name: str
    file_path: str
    content: str
    doc_type: str  # "description", "claims", "drawings", "unknown"
    
    def __len__(self) -> int:
        """
        Return content length in characters.
        
        Returns:
            int: Number of characters in content
        
        Example:
            >>> len(doc)
            5432
        """
        return len(self.content)
    
    def is_empty(self) -> bool:
        """
        Check if document is empty (no content or only whitespace).
        
        Returns:
            bool: True if empty, False otherwise
        
        Example:
            >>> doc.is_empty()
            False
        """
        return len(self.content.strip()) == 0
    
    def get_word_count(self) -> int:
        """
        Get approximate word count.
        
        Returns:
            int: Number of words (whitespace-separated tokens)
        
        Example:
            >>> doc.get_word_count()
            1234
        """
        return len(self.content.split())
    
    def get_preview(self, chars: int = 100) -> str:
        """
        Get preview of content (first N characters).
        
        Args:
            chars: Number of characters to preview (default: 100)
        
        Returns:
            str: Preview text with "..." if truncated
        
        Example:
            >>> doc.get_preview(50)
            'A system comprising a processor configured to...'
        """
        if len(self.content) <= chars:
            return self.content
        return self.content[:chars] + "..."
    
    def __str__(self) -> str:
        """
        String representation.
        
        Example:
            >>> str(doc)
            'PatentDocument(description.md, type=description, 5432 chars)'
        """
        return f"PatentDocument({self.file_name}, type={self.doc_type}, {len(self)} chars)"


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("MODELS.PY - USAGE EXAMPLES")
    print("="*70)
    
    # Example 1: Create a DetectionResult
    print("\n1. Creating DetectionResult:")
    result = DetectionResult(
        is_likely_ai_generated=True,
        confidence_score=0.732,
        risk_level="MEDIUM",
        feature_scores={
            "fingerprint": 0.68,
            "anchor_similarity": 0.85,
            "hallucination": 0.65,
            "drawing": 0.58
        },
        detailed_analysis={
            "fingerprint_analysis": {"score": 0.68, "findings": ["Uniform sentences"]},
            "anchor_analysis": {"similarity": 0.85, "findings": ["High similarity"]},
        },
        recommendations=[
            "🚨 CRITICAL: High anchor similarity",
            "⚠️ MEDIUM RISK: Moderate AI indicators"
        ],
        applied_rules=["anchor_method", "fingerprint_analysis"]
    )
    
    print(result)
    print(f"\nSummary: {result.get_summary()}")
    print(f"High Risk: {result.is_high_risk()}")
    print(f"Conclusive: {result.is_conclusive()}")
    
    # Example 2: Save to JSON
    print("\n2. Saving to JSON:")
    result.save_json("example_result.json")
    
    # Example 3: Create a PatentDocument
    print("\n3. Creating PatentDocument:")
    doc = PatentDocument(
        file_name="description.md",
        file_path="/path/to/description.md",
        content="A system comprising a processor configured to execute instructions...",
        doc_type="description"
    )
    
    print(doc)
    print(f"Length: {len(doc)} chars")
    print(f"Words: {doc.get_word_count()}")
    print(f"Empty: {doc.is_empty()}")
    print(f"Preview: {doc.get_preview(50)}")
    
    print("\n" + "="*70)
    print("✓ Models work correctly!")
    print("="*70)