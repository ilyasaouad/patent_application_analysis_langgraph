"""
core/ollama_client.py
=====================
Ollama client for local LLM inference
"""

import requests
from typing import Optional


class OllamaClient:
    """
    Local Ollama client - 100% privacy-focused.
    Handles all communication with local Ollama instance.
    """
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the Ollama model (e.g., "gpt-oss:120b-cloud")
            base_url: Base URL for Ollama API (default: localhost:11434)
        """
        self.model_name = model_name
        self.base_url = base_url
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama instance.
        
        Returns:
            bool: True if connected and model available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check if requested model is available
                for name in model_names:
                    if name.startswith(self.model_name.split(':')[0]):
                        return True
                
                print(f"⚠️ Model '{self.model_name}' not found in available models")
                return False
            
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Cannot connect to Ollama: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.1
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            str: Generated text or empty string on error
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"  ⚠️ Ollama error: HTTP {response.status_code}")
                return ""
                
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Ollama request timed out (>120s)")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Ollama call failed: {e}")
            return ""
        except Exception as e:
            print(f"  ⚠️ Unexpected error: {e}")
            return ""
    
    def get_available_models(self) -> list:
        """
        Get list of available models from Ollama.
        
        Returns:
            list: List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
            return []
        except Exception:
            return []
