# HCPCS Inference Service

## Overview
The HCPCS Inference Service infers HCPCS codes from policy text using modular inference methods (e.g., regex, lexical, LLM). The system is designed for **extensibility, reproducibility, and efficiency**, with clear separation between input handling, inference strategies, and output formatting.

---

## Key Design Principles

- **Modular Inference Methods**: Easily add or swap inference strategies without changing the pipeline interface.
- **Deterministic + Scalable**: Supports both lightweight (regex/lexical) and heavier (LLM/RAG) methods.
- **Reproducibility**: Structured outputs with provenance and consistent CLI behavior.
- **Efficiency via Caching**: Avoid recomputing identical inputs across runs.

---

## CLI Usage

### Core Behavior (Mutually Exclusive Input Modes)

You must provide **exactly one** of the following:

1. **Raw Text File**
2. **CSV + Row Selection**

---

### Example: CSV Mode

```bash
python3 run_pipeline.py \
  --input-csv src/tests/inputs/policies_cleaned.csv \
  --row 10 \
  --methods regex,lexical
```

---

### Example: Raw Text Mode

```bash
python3 run_pipeline.py \
  --input sample_policy.txt \
  --methods lexical
```

---

## Parameters

### Input Selection (Mutually Exclusive)

- `--input`  
  Path to a raw `.txt` file containing policy text.

- `--input-csv`  
  Path to a CSV file containing policy text.

- `--row`  
  Required when using `--input-csv`.  
  1-based index (excluding header). Example: `--row 2` selects the first data row.

- `--text-column`  
  Column name containing policy text in the CSV.  
  Default: `cleaned_policy_text`

---

### General Parameters

- `--base-dir`  
  Base directory used to resolve relative paths.  
  Default: directory of `run_pipeline.py`

- `--output`  
  Output JSON file path (resolved relative to `--base-dir` if not absolute).  
  Default: `src/tests/outputs/sample_output.json`

- `--methods`  
  Comma-separated list of inference methods.  
  Example: `regex,lexical,llm`  
  Allowed values defined in `ALLOWED_METHODS`.

---

## Output Schema

The pipeline returns structured JSON:

```json
[
    {
        "methods_run": [
            "lexical"
        ],
        "by_method": [
            {
                "method": "lexical",
                "output": {
                    "inferred_codes": [
                        {
                            "code": "R0070",
                            "confidence": 0.3766209273116631,
                            "justification": {
                                "reason": "Lexical similarity between policy text and HCPCS description.",
                                "details": "score=0.3766; matched_description=Transport portable x-ray"
                            },
                            "code_system": "HCPCS"
                        },
                        {
                            "code": "R0075",
                            "confidence": 0.3148132804018624,
                            "justification": {
                                "reason": "Lexical similarity between policy text and HCPCS description.",
                                "details": "score=0.3148; matched_description=Transport port x-ray multipl"
                            },
                            "code_system": "HCPCS"
                        }
                    ],
                    "audit": {
                        "timestamp": "2026-02-27T20:04:03.508294+00:00",
                        "method": "lexical",
                        "parameters": {
                            "method_version": "v1",
                            "top_k": 5,
                            "threshold": 0.25,
                            "hcpcs_sha": "d752b5543204d6b6a2db8bcec5e67733cb0e855b355bb740897609282589a2bd",
                            "vectorizer": {
                                "ngram_range": [
                                    1,
                                    2
                                ],
                                "stop_words": "english"
                            },
                            "cache_hit": false,
                            "cached_result_key": "b912c28c828f251e1b6af821df853e27652c5e1e6322fb3b9be3b92040907c63",
                            "cache_path": "src/tests/cache/cached_results.json"
                        }
                    }
                }
            }
        ],
        "output": {
            "inferred_codes": [
                {
                    "code": "R0070",
                    "confidence": 0.3766209273116631,
                    "justification": {
                        "reason": "Lexical similarity between policy text and HCPCS description.",
                        "details": "score=0.3766; matched_description=Transport portable x-ray"
                    },
                    "code_system": "HCPCS"
                },
                {
                    "code": "R0075",
                    "confidence": 0.3148132804018624,
                    "justification": {
                        "reason": "Lexical similarity between policy text and HCPCS description.",
                        "details": "score=0.3148; matched_description=Transport port x-ray multipl"
                    },
                    "code_system": "HCPCS"
                }
            ],
            "audit": {
                "timestamp": "2026-02-27T20:04:03.508622+00:00",
                "method": "orchestrator",
                "parameters": {
                    "methods": [
                        "lexical"
                    ],
                    "strategy_count": 1
                }
            }
        }
    }
]
```

### Schema Design Decisions

- **Flat + explicit fields** → easy to consume downstream
- **Confidence normalized (0–1)** → comparable across methods
- **Provenance object** → enables auditability and debugging
- **Extensible metadata** → supports future LLM/RAG outputs

---

## Caching System (`utils/cache.py`)

### Purpose
Avoid recomputing identical inputs across runs.

### How it works (high-level)
- Input text + method combination is hashed
- Result is stored in a local cache (e.g., JSON/disk-based)
- On subsequent runs:
  - If hash exists → return cached result
  - If not → compute and store

### Benefits
- Eliminates redundant LLM/API calls
- Speeds up repeated experimentation
- Reduces cost for expensive inference methods

### Example Scenario
Running:
```bash
--methods lexical,llm
```

If the lexical output remains consistent across runs, it can be served directly from cache, while only the LLM step is recomputed when needed.

In a production setting, cache usage could be scoped per user (e.g., size limits tied to a user token). This would enable surfacing frequently relevant results based on prior interactions. A simple feedback mechanism—such as a “Was this suggestion helpful?” prompt—could capture user input (thumbs up/down) to support manual review and continuous improvement. Over time, this feedback can inform prioritization and weighting of inference strategies.

---

## Utility Modules

### `utils/parser.py`
- Parses CLI method strings → validated list
- Enforces allowed inference methods
- Converts outputs to JSON-safe format (`to_jsonable`)

### `utils/cache.py`
- Handles hash generation and lookup
- Abstracts storage layer (can be extended to Redis/S3)

### `utils/logging.py`
- Standardized logging interface
- Ensures consistent debug + audit output
- Can be extended for structured logging (JSON logs)

---

## Directory Structure

```
src/
  services/
    inference/
      runner.py              # Orchestration Initialization
      orchestrator.py        # Orchestration layer
      methods/         # Individual inference strategies
    llm/
      client.py        # mock GPT
  models/              # Output schemas
  utils/
    cache.py
    logging.py
    parser.py
  tests/
    inputs/     # reference files
    outputs/    # response json
    cache/      # json of recent requests. in prod, could limit to user

run_pipeline.py        # CLI entrypoint
```

### Extending Methods

To add a new inference method:
1. Implement it under `services/inference/methods/`
2. Register it in `ALLOWED_METHODS`
3. Ensure it returns schema-compliant output

No changes needed to CLI or pipeline orchestration.

---

## Environment Setup

### Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### `.env` Configuration

Not really needed for this demo since of mock output, but will be used for:
- API keys (e.g., OpenAI; right now we just use a mock output for LLM)
- Environment-specific configs (prod vs dev base dir)

---

## My Scalability Considerations

- **Method-level parallelism** can be added (each method independent)
- **Caching layer** can be upgraded to distributed store (Redis)
- **Batch processing** can extend CSV mode beyond single-row selection
- **Stateless CLI design** → easy to containerize

---

## CI/CD & Reproducibility

### Reproducibility
- Deterministic input selection (`--row`, `--methods`)
- Structured outputs
- Cache ensures stable repeated runs

### CI/CD Potential
- Add test cases using fixed inputs
- Validate output schema + method behavior
- Lint + type checking
- Snapshot-based regression tests

---

## Future Enhancements

- Batch CSV processing
- Async / parallel inference execution
- Pluggable cache backends (Redis, S3)
- API layer (FastAPI) on top of CLI
- Versioned schema outputs

---

## License
MIT License
