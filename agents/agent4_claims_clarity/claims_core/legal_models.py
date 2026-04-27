"""
core/legal_models.py
====================
Data models for patent legal analysis results
NIPO examination standards
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class EnablementResult:
    """
    Enablement analysis result (Norwegian Patents Act § 8 (2)).
    
    Attributes:
        status: "ENABLED" or "NOT_ENABLED"
        issues: List of enablement issues found
        missing_elements: List of missing technical elements
        technical_deficiencies: List of technical deficiencies
        reproducibility_score: 0.0-1.0 score
        confidence: "HIGH", "MEDIUM", or "LOW"
    """
    status: str  # "ENABLED" or "NOT_ENABLED"
    status_reason: str
    issues: List[str]
    missing_elements: List[str]
    technical_deficiencies: List[str]
    reproducibility_score: float
    confidence: str
    detailed_issues: List[Dict[str, Any]]
    guideline_version: Optional[str] = None
    
    def is_enabled(self) -> bool:
        """Check if invention is sufficiently enabled."""
        return self.status == "ENABLED"
    
    def has_critical_issues(self) -> bool:
        """Check if there are critical enablement issues."""
        return len(self.missing_elements) > 0 or len(self.technical_deficiencies) > 2


@dataclass
class ClarityResult:
    """
    Clarity analysis result (Norwegian Patents Act § 8 (2)).
    
    Attributes:
        status: "CLEAR" or "UNCLEAR"
        issues: List of clarity issues
        vague_terms: List of vague/subjective terms
        undefined_terms: List of undefined technical terms
        ambiguous_phrases: List of ambiguous phrases
        clarity_score: 0.0-1.0 score
        confidence: "HIGH", "MEDIUM", or "LOW"
    """
    status: str  # "CLEAR" or "UNCLEAR"
    status_reason: str
    issues: List[str]
    vague_terms: List[str]
    undefined_terms: List[str]
    ambiguous_phrases: List[str]
    clarity_score: float
    confidence: str
    detailed_issues: List[Dict[str, Any]]
    guideline_version: Optional[str] = None
    
    def is_clear(self) -> bool:
        """Check if claims are sufficiently clear."""
        return self.status == "CLEAR"
    
    def has_vague_language(self) -> bool:
        """Check if there are vague terms."""
        return len(self.vague_terms) > 0


@dataclass
class SupportResult:
    """
    Support analysis result (Norwegian Patents Act § 8 (2)).
    
    Attributes:
        status: "SUPPORTED" or "NOT_SUPPORTED"
        issues: List of support issues
        unsupported_elements: List of unsupported claim elements
        broader_than_description: List of features broader than description
        missing_embodiments: List of missing embodiments
        support_score: 0.0-1.0 score
        confidence: "HIGH", "MEDIUM", or "LOW"
    """
    status: str  # "SUPPORTED" or "NOT_SUPPORTED"
    status_reason: str
    issues: List[str]
    unsupported_elements: List[str]
    broader_than_description: List[str]
    missing_embodiments: List[str]
    support_score: float
    confidence: str
    detailed_issues: List[Dict[str, Any]]
    guideline_version: Optional[str] = None
    
    def is_supported(self) -> bool:
        """Check if claims are sufficiently supported."""
        return self.status == "SUPPORTED"
    
    def has_scope_issues(self) -> bool:
        """Check if claim scope is broader than description."""
        return len(self.broader_than_description) > 0


@dataclass
class LegalAnalysisResult:
    """
    Complete patent legal analysis result.
    
    Combines enablement, clarity, and support analysis with overall assessment.
    
    Attributes:
        enablement: EnablementResult
        clarity: ClarityResult
        support: SupportResult
        risk_level: "LOW", "MEDIUM", or "HIGH"
        summary: Brief summary of main issues
        critical_issues: List of critical issues
        recommendations: List of actionable recommendations
        examination_decision: "GRANT", "OBJECT", or "FURTHER_EXAMINATION"
        metadata: Optional metadata (timestamp, version, etc.)
    """
    enablement: EnablementResult
    clarity: ClarityResult
    support: SupportResult
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    summary: str
    critical_issues: List[str]
    recommendations: List[str]
    examination_decision: str  # "GRANT", "OBJECT", "FURTHER_EXAMINATION"
    formal_report: str = ""
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "legal_framework": "NIPO",
                "articles": ["Patent Act § 8 (2)"]
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "enablement": asdict(self.enablement),
            "clarity": asdict(self.clarity),
            "support": asdict(self.support),
            "overall_assessment": {
                "risk_level": self.risk_level,
                "summary": self.summary,
                "critical_issues": self.critical_issues,
                "recommendations": self.recommendations,
                "examination_decision": self.examination_decision
            },
            "formal_report": self.formal_report,
            "metadata": self.metadata
        }
    
    def save_json(self, output_path: str) -> None:
        """Save result to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Legal analysis saved to: {output_path}")
        except Exception as e:
            print(f"✗ Error saving legal analysis: {e}")
    
    def is_grantable(self) -> bool:
        """Check if patent is likely grantable."""
        return self.examination_decision == "GRANT"
    
    def requires_objection(self) -> bool:
        """Check if objections should be raised."""
        return self.examination_decision == "OBJECT"
    
    def get_legal_violations(self) -> List[str]:
        """Get list of legal violations."""
        violations = []
        
        if not self.enablement.is_enabled():
            violations.append("Patent Act § 8 (2) - Insufficient enablement")
        
        if not self.clarity.is_clear():
            violations.append("Patent Act § 8 (2) - Unclear claims")
        
        if not self.support.is_supported():
            violations.append("Patent Act § 8 (2) - Insufficient support")
        
        return violations
    
    def get_summary_report(self) -> str:
        """Get human-readable summary report."""
        report = []
        report.append("="*70)
        report.append("PATENT LEGAL ANALYSIS - NIPO")
        report.append("="*70)
        report.append(f"\nEXAMINATION DECISION: {self.examination_decision}")
        report.append(f"RISK LEVEL: {self.risk_level}")
        report.append(f"\n{self.summary}")
        
        if self.formal_report:
            report.append("\n" + "="*70)
            report.append("FORMAL EXAMINATION REPORT")
            report.append("="*70)
            report.append(f"\n{self.formal_report}\n")
            
        report.append(f"\n{'='*70}")
        report.append("ENABLEMENT (§ 8)")
        report.append(f"{'='*70}")
        report.append(f"Status: {self.enablement.status}")
        if getattr(self.enablement, "status_reason", ""):
            report.append(f"Reason: {self.enablement.status_reason}")
        report.append(f"Reproducibility: {self.enablement.reproducibility_score:.1%}")
        if self.enablement.missing_elements:
            report.append("\nMissing Elements:")
            for elem in self.enablement.missing_elements:
                report.append(f"  • {elem}")
        
        report.append(f"\n{'='*70}")
        report.append("CLARITY (§ 8)")
        report.append(f"{'='*70}")
        report.append(f"Status: {self.clarity.status}")
        if getattr(self.clarity, "status_reason", ""):
            report.append(f"Reason: {self.clarity.status_reason}")
        report.append(f"Clarity Score: {self.clarity.clarity_score:.1%}")
        if self.clarity.vague_terms:
            report.append("\nVague Terms:")
            for term in self.clarity.vague_terms:
                report.append(f"  • {term}")
        
        report.append(f"\n{'='*70}")
        report.append("SUPPORT (§ 8)")
        report.append(f"{'='*70}")
        report.append(f"Status: {self.support.status}")
        if getattr(self.support, "status_reason", ""):
            report.append(f"Reason: {self.support.status_reason}")
        report.append(f"Support Score: {self.support.support_score:.1%}")
        if self.support.unsupported_elements:
            report.append("\nUnsupported Elements:")
            for elem in self.support.unsupported_elements:
                report.append(f"  • {elem}")
                
        # Detailed Grounded Issues
        def append_detailed_issues(domain_name, detailed_issues):
            if detailed_issues:
                report.append(f"\n--- Detailed {domain_name} Violations ---")
                for issue in detailed_issues:
                    observation = issue.get('observation', 'N/A')
                    legal_mapping = issue.get('legal_mapping', 'N/A')
                    confidence = issue.get('confidence_level', 'N/A')
                    amendment = issue.get('amendment', 'N/A')
                    severity = issue.get('severity', 'N/A')
                    
                    report.append(f"[{severity}] Confidence: {confidence}")
                    report.append(f"          Observation: {observation}")
                    report.append(f"          Legal Mapping: {legal_mapping}")
                    report.append(f"          Suggestion: {amendment}")
                    
        append_detailed_issues("Enablement", getattr(self.enablement, "detailed_issues", []))
        append_detailed_issues("Clarity", getattr(self.clarity, "detailed_issues", []))
        append_detailed_issues("Support", getattr(self.support, "detailed_issues", []))
        
        if self.critical_issues:
            report.append(f"\n{'='*70}")
            report.append("CRITICAL ISSUES")
            report.append(f"{'='*70}")
            for issue in self.critical_issues:
                report.append(f"  🚨 {issue}")
        
        if self.recommendations:
            report.append(f"\n{'='*70}")
            report.append("RECOMMENDATIONS")
            report.append(f"{'='*70}")
            for i, rec in enumerate(self.recommendations, 1):
                report.append(f"  {i}. {rec}")
        
        report.append(f"\n{'='*70}\n")
        
        return "\n".join(report)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"LegalAnalysisResult(\n"
            f"  Decision: {self.examination_decision}\n"
            f"  Risk: {self.risk_level}\n"
            f"  Enablement: {self.enablement.status}\n"
            f"  Clarity: {self.clarity.status}\n"
            f"  Support: {self.support.status}\n"
            f")"
        )
