# src/services/inference/runner.py
from __future__ import annotations

from typing import List, Dict, Any
from src.services.inference.orchestrator import InferenceOrchestrator

def run_pipeline_texts(policy_texts: List[str]) -> List[Dict[str, Any]]:
    orchestrator = InferenceOrchestrator()
    results: List[Dict[str, Any]] = []

    for policy_text in policy_texts:
        policy_text = policy_text.strip()
        if not policy_text:
            continue
        results.append(orchestrator.run_inference(policy_text))

    return results