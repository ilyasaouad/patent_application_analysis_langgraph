import os
from pathlib import Path
from typing import Optional

class GuidelineLoader:
    """
    Utility class to load EPO/NIPO guidelines from the resources/guidelines directory.
    """
    
    def __init__(self, guidelines_path: Optional[str] = None):
        if guidelines_path:
            self.guidelines_dir = Path(guidelines_path)
        else:
            # Default to the resources/guidelines inside claims_analyse
            current_dir = Path(__file__).parent.parent.absolute()
            self.guidelines_dir = current_dir / "resources" / "guidelines"
            
    def load_guideline(self, filename: str) -> str:
        """
        Load a specific guideline text file by name.
        """
        file_path = self.guidelines_dir / filename
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
        except Exception as e:
            print(f"Error loading guideline {filename}: {e}")
            return ""
            
    def get_clarity_guidelines(self) -> str:
        return self.load_guideline("clarity.txt")
        
    def get_enablement_guidelines(self) -> str:
        return self.load_guideline("enablement.txt")
        
    def get_support_guidelines(self) -> str:
        return self.load_guideline("support.txt")
