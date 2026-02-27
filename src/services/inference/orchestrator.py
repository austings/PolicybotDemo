import os
from dotenv import load_dotenv

from src.services.inference.methods.llm_inference import LLMInference
from src.services.inference.methods.rag_inference import RAGInference
from src.services.inference.methods.lexical_inference import LexInference
load_dotenv()

class InferenceOrchestrator:
    def __init__(self, methods: list[str]):
        if not methods:
            raise ValueError("methods must be a non-empty list")
        self.methods = methods
        self.strategies = [self._make_strategy(m) for m in methods]

    def _make_strategy(self, method: str):
        method = method.lower()

        if method == "llm":
            endpoint = os.getenv("LLM_ENDPOINT", "mock")
            return LLMInference(endpoint=endpoint)

        if method == "rag":
            return RAGInference()
        
        if method == "lexical":
            return LexInference()
        
        # TODO: add "regex", "lexical" here as you implement them
        raise ValueError(f"Unknown inference method: {method}")

    def run_inference(self, policy_text: str):
        """
        Run each method in order and return method-scoped outputs.
        This is audit-friendly and supports ensembling later.
        """
        results = []
        for method, strategy in zip(self.methods, self.strategies):
            out = strategy.infer(policy_text)
            results.append({"method": method, "output": out})

        return {
            "methods_run": self.methods,
            "by_method": results
        }