# src/utils/cache.py
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def make_cache_key(*, method: str, policy_text: str, params: Dict[str, Any]) -> str:
    """
    Cache key depends on:
      - method
      - normalized text hash
      - params (sorted JSON)
    """
    payload = {
        "method": method,
        "policy_text_sha": sha256_text(policy_text),
        "params": params,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()