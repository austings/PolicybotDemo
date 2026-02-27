# src/services/inference/runner.py
from __future__ import annotations

from typing import List, Dict, Any
from src.services.inference.orchestrator import InferenceOrchestrator

def run_pipeline_texts(policy_texts: List[str], methods: List[str]) -> List[Dict[str, Any]]:
    """
    Run inference for each policy text using the provided methods in order.
    Returns one result object per input policy text.
    """
    orchestrator = InferenceOrchestrator(methods=methods)
    results: List[Dict[str, Any]] = []

    for policy_text in policy_texts:
        text = policy_text.strip()
        if not text:
            continue
        results.append(orchestrator.run_inference(text))

    return results