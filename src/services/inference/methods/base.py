# src/services/inference/methods/base.py
from src.models.schemas import InferenceResult

class InferenceMethod:
    def infer(self, policy_text: str) -> InferenceResult:
        raise NotImplementedError

