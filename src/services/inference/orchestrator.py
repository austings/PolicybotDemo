import os
from dotenv import load_dotenv

from src.services.inference.methods.llm_inference import LLMInference
from src.services.inference.methods.rag_inference import RAGInference

# Load .env if it exists (no error if missing)
load_dotenv()

class InferenceOrchestrator:
    def __init__(self, method: str = None):
        # Allow override, else use env, else default to llm
        self.method = method or os.getenv("INFERENCE_METHOD", "llm")
        self.inference_strategy = self._select_inference_method()

    def _select_inference_method(self):
        if self.method == "llm":
            endpoint = os.getenv("LLM_ENDPOINT", "mock")
            return LLMInference(endpoint=endpoint)

        elif self.method == "rag":
            return RAGInference()

        else:
            raise ValueError(f"Unknown inference method: {self.method}")

    def run_inference(self, policy_text: str):
        return self.inference_strategy.infer(policy_text)