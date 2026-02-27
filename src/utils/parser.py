# src/utils/parser.py

import argparse

ALLOWED_METHODS = ["lexical","llm", "rag"]

def to_jsonable(x):
    if hasattr(x, "model_dump"):
        return x.model_dump()
    if isinstance(x, list):
        return [to_jsonable(i) for i in x]
    if isinstance(x, dict):
        return {k: to_jsonable(v) for k, v in x.items()}
    return x

def parse_methods(raw: str) -> list[str]:
    methods = [m.strip().lower() for m in raw.split(",") if m.strip()]

    if not methods:
        raise argparse.ArgumentTypeError("methods cannot be empty")

    unknown = [m for m in methods if m not in ALLOWED_METHODS]
    if unknown:
        raise argparse.ArgumentTypeError(
            f"Unknown methods: {unknown}. Allowed: {ALLOWED_METHODS}"
        )

    # de-dupe, preserve order
    seen = set()
    out = []
    for m in methods:
        if m not in seen:
            seen.add(m)
            out.append(m)

    return out