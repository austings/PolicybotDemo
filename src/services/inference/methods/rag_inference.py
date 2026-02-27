from __future__ import annotations

from src.services.inference.methods.base import InferenceMethod
from src.models.schemas import InferenceResult, InferredCode, Justification, Audit, now_iso


class RAGInference(InferenceMethod):
    def __init__(self, top_k: int = 5, index_version: str = "mock-index-v1"):
        self.top_k = top_k
        self.index_version = index_version

    def infer(self, policy_text: str) -> InferenceResult:
        # Mocked response for demonstration purposes (replace with real retrieval later)
        inferred = [
            InferredCode(
                code="A1234",
                confidence=0.85,
                justification=Justification(
                    reason="Matched keywords related to service A.",
                    details="Mock RAG hit: 'service A' found in retrieved context."
                ),
            ),
            InferredCode(
                code="B5678",
                confidence=0.75,
                justification=Justification(
                    reason="Contextual relevance based on retrieved policy context.",
                    details="Mock RAG: similarity score above threshold."
                ),
            ),
        ]

        audit = Audit(
            timestamp=now_iso(),
            method="rag",
            parameters={
                "top_k": self.top_k,
                "index_version": self.index_version,
                "mode": "mock"
            },
        )

        return InferenceResult(inferred_codes=inferred, audit=audit)