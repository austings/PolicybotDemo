import argparse
import json
from pathlib import Path

from src.services.inference.runner import run_pipeline_texts
from src.utils.parser import parse_methods, ALLOWED_METHODS, to_jsonable


BASE_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Run the HCPCS inference pipeline.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(BASE_DIR / "src/tests/inputs/sample_policy.txt"),
        help="Path to the input policy text file."
    )

    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR / "src/tests/outputs/sample_output.json"),
        help="Path to the output JSON file for inferred HCPCS codes."
    )

    parser.add_argument(
        "--methods",
        type=parse_methods,
        default=parse_methods("lexical"),   # sensible default baseline
        help=f"Comma-separated inference methods. Allowed: {ALLOWED_METHODS}. Example: lexical,llm"
    )

    args = parser.parse_args()

    print("HCPCS inference pipeline running")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")

    # Run the inference pipeline
    with open(args.input, "r", encoding="utf-8") as f:
        policy_texts = [f.read()]

    result = run_pipeline_texts(policy_texts, args.methods)

    # Write the result to the output file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as outfile:
        json.dump(to_jsonable(result), outfile, indent=4)

    print(f"Inference results saved to {args.output}")

if __name__ == "__main__":
    main()