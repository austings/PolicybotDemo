from __future__ import annotations

from typing import Any, Dict, Optional
import os

try:
    import requests
except ImportError:
    requests = None  # lets you run in mock mode without requests installed


class LLMClient:
    """
    Minimal client for an LLM service.

    For this exercise, default to MOCK mode so the pipeline runs locally.
    When you have a real endpoint, set LLM_ENDPOINT to an http(s) URL.
    """

    def __init__(self, endpoint: Optional[str] = None, timeout_s: float = 10.0):
        # If not provided, read from env; default to "mock" (no network).
        self.endpoint = endpoint or os.getenv("LLM_ENDPOINT", "mock")
        self.timeout_s = timeout_s

    def query(self, policy_text: str) -> Dict[str, Any]:
        # Mock mode: no network calls, deterministic stub response.
        if self.endpoint == "mock":
            return {
                "codes": [
                    {
                        "code": "A0428",
                        "confidence": 0.7,
                        "justification": "Mock LLM: ambulance transport-related language detected."
                    }
                ],
                "model": "mock-llm-v1"
            }

        if requests is None:
            raise RuntimeError("requests is required for non-mock LLM_ENDPOINT")

        payload = {"text": policy_text}
        resp = requests.post(self.endpoint, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()