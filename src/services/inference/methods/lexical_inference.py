# src/services/inference/methods/lexical_inference.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, List
import pandas as pd

from src.services.inference.methods.base import InferenceMethod
from src.models.schemas import InferenceResult, InferredCode, Justification, Audit, now_iso
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.cache import make_cache_key, sha256_file, normalize_text


class LexInference(InferenceMethod):
    """
    Lexical inference (stub scoring for now) + JSON-file caching.
    Cache format:
      {
        "version": "v1",
        "entries": {
           "<cache_key>": { ...InferenceResult dict... }
        }
      }
    """

    METHOD_NAME = "lexical"
    METHOD_VERSION = "v1"

    def __init__(
        self,
        cache_path: str | Path = "src/tests/cache/cached_results.json",
        hcpcs_path: str | Path = "src/tests/inputs/hcpcs.csv",
        top_k: int = 5,
        threshold: float = 0.25,
    ):
        self.cache_path = Path(cache_path)
        self.hcpcs_path = Path(hcpcs_path)
        self.top_k = top_k
        self.threshold = threshold
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        # load hcpcs table once (v1)
        self._hcpcs_df = pd.read_csv(self.hcpcs_path)
        if "code" not in self._hcpcs_df.columns or "description" not in self._hcpcs_df.columns:
            raise ValueError("hcpcs.csv must have columns: code, description")

        self._codes = self._hcpcs_df["code"].astype(str).tolist()
        self._descs = self._hcpcs_df["description"].astype(str).tolist()

        # build TF-IDF index once (v1)
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        self._X = self._vectorizer.fit_transform([normalize_text(d) for d in self._descs])

        self._hcpcs_sha = sha256_file(self.hcpcs_path)

    def infer(self, policy_text: str) -> InferenceResult:
        params = {
            "method_version": self.METHOD_VERSION,
            "top_k": self.top_k,
            "threshold": self.threshold,
            "hcpcs_sha": self._hcpcs_sha,
        }
        cache_key = make_cache_key(method=self.METHOD_NAME, policy_text=policy_text, params=params)

        store = self._load_cache_store()
        cached = store["entries"].get(cache_key)

        if cached is not None:
            # cached is already an InferenceResult-like dict -> rebuild Pydantic model
            result = InferenceResult(**cached)
            # annotate audit
            result.audit.parameters["cache_hit"] = True
            result.audit.parameters["cached_result_key"] = cache_key
            result.audit.parameters["cache_path"] = str(self.cache_path)
            return result

        # Cache miss: compute
        result = self._compute(policy_text)

        # annotate audit for miss
        result.audit.parameters["cache_hit"] = False
        result.audit.parameters["cached_result_key"] = cache_key
        result.audit.parameters["cache_path"] = str(self.cache_path)

        # write-through cache
        store["entries"][cache_key] = result.model_dump()
        self._save_cache_store(store)

        return result

    def _compute(self, policy_text: str) -> InferenceResult:
        text = normalize_text(policy_text)
        q = self._vectorizer.transform([text])
        sims = cosine_similarity(q, self._X).ravel()  # shape: (num_codes,)

        # get top candidates
        top_idx = sims.argsort()[::-1][: self.top_k]

        inferred: List[InferredCode] = []
        for i in top_idx:
            score = float(sims[i])
            if score < self.threshold:
                continue

            # confidence mapping: keep it simple and monotonic
            # (cosine similarity is already 0..1 for TF-IDF cosine)
            confidence = max(0.0, min(1.0, score))

            inferred.append(
                InferredCode(
                    code=str(self._codes[i]),
                    confidence=confidence,
                    justification=Justification(
                        reason="Lexical similarity between policy text and HCPCS description.",
                        details=f"score={score:.4f}; matched_description={self._descs[i][:200]}"
                    ),
                )
            )

        audit = Audit(
            timestamp=now_iso(),
            method=self.METHOD_NAME,
            parameters={
                "method_version": self.METHOD_VERSION,
                "top_k": self.top_k,
                "threshold": self.threshold,
                "hcpcs_sha": self._hcpcs_sha,
                "vectorizer": {"ngram_range": [1, 2], "stop_words": "english"},
            },
        )
        return InferenceResult(inferred_codes=inferred, audit=audit)

    def _load_cache_store(self) -> Dict[str, Any]:
        if not self.cache_path.exists():
            return {"version": "v1", "entries": {}}

        try:
            with self.cache_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {"version": "v1", "entries": {}}
            data.setdefault("version", "v1")
            data.setdefault("entries", {})
            if not isinstance(data["entries"], dict):
                data["entries"] = {}
            return data
        except json.JSONDecodeError:
            # If file is corrupted, don't crash the pipeline
            return {"version": "v1", "entries": {}}

    def _save_cache_store(self, store: Dict[str, Any]) -> None:
        tmp = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
        tmp.replace(self.cache_path)