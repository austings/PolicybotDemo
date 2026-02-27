import os
from dotenv import load_dotenv
from src.models.schemas import InferenceResult, Audit, now_iso
from src.services.inference.methods.llm_inference import LLMInference
from src.services.inference.methods.rag_inference import RAGInference
from src.services.inference.methods.regex_inference import RegexInference
from src.services.inference.methods.lexical_inference import LexInference

load_dotenv()

class InferenceOrchestrator:
    def __init__(self, methods: list[str]):
        if not methods:
            raise ValueError("methods must be a non-empty list")
        self.methods = methods
        self.strategies = [self._make_strategy(m) for m in methods]

    def _merge_results(self, method_results):
        merged = {}  # (code_system, code) -> InferredCode
        for mr in method_results:
            for ic in mr.inferred_codes:
                key = (getattr(ic, "code_system", "HCPCS") or "HCPCS", ic.code)
                if key not in merged or ic.confidence > merged[key].confidence:
                    merged[key] = ic

        out = list(merged.values())
        out.sort(key=lambda ic: (getattr(ic, "code_system", "HCPCS") or "HCPCS", ic.code))
        return out

    def _make_strategy(self, method: str):
        method = method.lower()

        if method == "llm":
            endpoint = os.getenv("LLM_ENDPOINT", "mock")
            return LLMInference(endpoint=endpoint)

        if method == "rag":
            return RAGInference()
        
        if method == "regex":
            return RegexInference()

        if method == "lexical":
            cache_path = os.getenv("LEXICAL_CACHE_PATH", "src/tests/cache/cached_results.json")
            hcpcs_path = os.getenv("HCPCS_PATH", "src/tests/inputs/hcpcs.csv")
            return LexInference(cache_path=cache_path, hcpcs_path=hcpcs_path)

        raise ValueError(f"Unknown inference method: {method}")

    def run_inference(self, policy_text: str):
        method_outputs = [s.infer(policy_text) for s in self.strategies]
        final_codes = self._merge_results(method_outputs)

        return {
            "methods_run": self.methods,
            "by_method": [{"method": m, "output": r} for m, r in zip(self.methods, method_outputs)],
            "output": InferenceResult(
                inferred_codes=final_codes,
                audit=Audit(
                    timestamp=now_iso(),
                    method="orchestrator",
                    parameters={"methods": self.methods, "strategy_count": len(self.strategies)},
                ),
            ),
        }