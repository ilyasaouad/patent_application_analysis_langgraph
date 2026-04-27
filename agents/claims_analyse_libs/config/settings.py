"""
config/settings.py
==================
Configuration settings for AI Patent Analyzer
"""

import os
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalyzerConfig:
    """Centralized configuration with sensible defaults."""
    
    # ========================================================================
    # LLM Settings
    # ========================================================================
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gpt-oss:120b-cloud"
    CLOUD_MODEL: str = "gpt-oss:120b-cloud"
    LLM_PROVIDER: str = "ollama"  # "ollama" or "gpt-oss"
    API_KEY: str = ""
    
    # ========================================================================
    # Analysis Settings
    # ========================================================================
    MAX_INPUT_CHARS: int = 4000
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.1  # Low for consistent analysis
    
    # ========================================================================
    # Detection Thresholds
    # ========================================================================
    AI_DETECTION_THRESHOLD: float = 0.6
    HIGH_RISK_THRESHOLD: float = 0.75
    MEDIUM_RISK_THRESHOLD: float = 0.60
    LOW_RISK_THRESHOLD: float = 0.40
    
    # ========================================================================
    # Phase Weights (must sum to 1.0)
    # ========================================================================
    WEIGHT_FINGERPRINT: float = 0.30     # Stylometric analysis
    WEIGHT_ANCHOR: float = 0.40          # Strongest signal
    WEIGHT_HALLUCINATION: float = 0.20   # Technical validation
    WEIGHT_DRAWING: float = 0.10         # Drawing consistency
    
    # ========================================================================
    # File Matching Patterns
    # ========================================================================
    DESCRIPTION_PATTERNS: list = None    # ["description", "describtion"]
    CLAIMS_PATTERNS: list = None         # ["claim"]
    DRAWING_PATTERNS: list = None        # ["drawing"]
    
    def __post_init__(self):
        """Set default patterns after initialization."""
        if self.DESCRIPTION_PATTERNS is None:
            self.DESCRIPTION_PATTERNS = ["description", "describtion"]
        if self.CLAIMS_PATTERNS is None:
            self.CLAIMS_PATTERNS = ["claim"]
        if self.DRAWING_PATTERNS is None:
            self.DRAWING_PATTERNS = ["drawing"]
    
    @classmethod
    def from_settings_file(cls, settings_path: Optional[str] = None) -> "AnalyzerConfig":
        """
        Load config from external JSON file if available, otherwise use defaults.
        
        Args:
            settings_path: Path to settings JSON file
        
        Returns:
            AnalyzerConfig instance
        """
        if settings_path and os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
            except Exception as e:
                print(f"⚠️ Could not load settings file: {e}")
                print(f"   Using default configuration")
        
        return cls()
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        # Check weights sum to 1.0
        total_weight = (
            self.WEIGHT_FINGERPRINT +
            self.WEIGHT_ANCHOR +
            self.WEIGHT_HALLUCINATION +
            self.WEIGHT_DRAWING
        )
        
        if abs(total_weight - 1.0) > 0.001:
            print(f"⚠️ Warning: Phase weights sum to {total_weight:.3f}, not 1.0")
            return False
        
        # Check thresholds are in valid range
        if not (0 <= self.AI_DETECTION_THRESHOLD <= 1):
            print(f"⚠️ Warning: AI_DETECTION_THRESHOLD must be between 0 and 1")
            return False
        
        return True
    
    def save_to_file(self, output_path: str) -> None:
        """Save configuration to JSON file."""
        config_dict = {
            "OLLAMA_URL": self.OLLAMA_URL,
            "OLLAMA_MODEL": self.OLLAMA_MODEL,
            "LLM_PROVIDER": self.LLM_PROVIDER,
            "MAX_INPUT_CHARS": self.MAX_INPUT_CHARS,
            "MAX_TOKENS": self.MAX_TOKENS,
            "TEMPERATURE": self.TEMPERATURE,
            "AI_DETECTION_THRESHOLD": self.AI_DETECTION_THRESHOLD,
            "HIGH_RISK_THRESHOLD": self.HIGH_RISK_THRESHOLD,
            "MEDIUM_RISK_THRESHOLD": self.MEDIUM_RISK_THRESHOLD,
            "LOW_RISK_THRESHOLD": self.LOW_RISK_THRESHOLD,
            "WEIGHT_FINGERPRINT": self.WEIGHT_FINGERPRINT,
            "WEIGHT_ANCHOR": self.WEIGHT_ANCHOR,
            "WEIGHT_HALLUCINATION": self.WEIGHT_HALLUCINATION,
            "WEIGHT_DRAWING": self.WEIGHT_DRAWING
        }
        
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✓ Configuration saved to: {output_path}")


# Example configuration presets

class StrictConfig(AnalyzerConfig):
    """Stricter thresholds for high-stakes analysis."""
    AI_DETECTION_THRESHOLD: float = 0.55
    HIGH_RISK_THRESHOLD: float = 0.70


class LenientConfig(AnalyzerConfig):
    """More lenient thresholds to reduce false positives."""
    AI_DETECTION_THRESHOLD: float = 0.70
    HIGH_RISK_THRESHOLD: float = 0.80


class FastConfig(AnalyzerConfig):
    """Faster analysis with reduced text processing."""
    MAX_INPUT_CHARS: int = 2000
    MAX_TOKENS: int = 1024
