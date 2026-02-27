from __future__ import annotations

from typing import Any, Dict
from src.services.inference.methods.base import InferenceMethod
from src.services.llm.client import LLMClient
from src.models.schemas import InferenceResult, InferredCode, Justification, Audit, now_iso

class LLMInference(InferenceMethod):
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or "mock"
        self.llm_client = LLMClient(endpoint=self.endpoint)

    def infer(self, policy_text: str) -> InferenceResult:
        response = self.llm_client.query(policy_text)
        return self._to_result(response)

    def _to_result(self, response: Dict[str, Any]) -> InferenceResult:
        codes = []
        for c in response.get("codes", []):
            # if justification comes back as a string, normalize it to Justification
            justification = c.get("justification", "")
            if isinstance(justification, str):
                just_obj = Justification(reason=justification)
            else:
                # if you later return {reason, details}
                just_obj = Justification(**justification)

            codes.append(
                InferredCode(
                    code=c["code"],
                    confidence=float(c["confidence"]),
                    justification=just_obj
                )
            )

        audit = Audit(
            timestamp=response.get("timestamp") or now_iso(),
            method="llm",
            parameters={
                "endpoint": self.endpoint,
                "model": response.get("model", "unknown"),
                "mode": "mock" if self.endpoint == "mock" else "remote",
            },
        )

        return InferenceResult(inferred_codes=codes, audit=audit)