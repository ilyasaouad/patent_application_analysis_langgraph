"""
OllamaClient — thin wrapper around the Ollama HTTP API.
Mirrors the client from MCP_cpc_classes, adapted for standalone agent use.
"""

import json
import urllib.request
import urllib.error
from typing import Optional


class OllamaClient:
    """
    Sends chat requests to a locally running Ollama instance.
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:120b-cloud",
        base_url: str = "http://localhost:11434",
        timeout: int = 300,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls": 0,
            "total_duration_ns": 0,
        }

    @property
    def usage(self) -> dict:
        """Return cumulative token usage across all calls."""
        return dict(self._usage)

    def _record_usage(self, response_json: dict):
        """Extract and accumulate token counts from an Ollama response."""
        prompt_tokens = response_json.get("prompt_eval_count", 0)
        completion_tokens = response_json.get("eval_count", 0)
        duration = response_json.get("total_duration", 0)
        self._usage["prompt_tokens"] += prompt_tokens
        self._usage["completion_tokens"] += completion_tokens
        self._usage["total_tokens"] += prompt_tokens + completion_tokens
        self._usage["calls"] += 1
        self._usage["total_duration_ns"] += duration

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> Optional[str]:
        """
        Send a system + user message to the model and return the response text.
        """
        endpoint = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Could not reach Ollama at {self.base_url}. "
                f"Is Ollama running? Detail: {e}"
            ) from e

        try:
            body = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ollama returned non-JSON response: {raw[:200]}") from e

        self._record_usage(body)

        try:
            return body["message"]["content"]
        except (KeyError, TypeError):
            if "response" in body:
                return body["response"]
            raise RuntimeError(
                f"Unexpected Ollama response structure: {str(body)[:300]}"
            )

    def embeddings(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generate a vector embedding for the given text."""
        endpoint = f"{self.base_url}/api/embeddings"
        payload = {"model": model, "prompt": text}
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["embedding"]
        except Exception as e:
            raise RuntimeError(f"Embedding call failed: {e}")
