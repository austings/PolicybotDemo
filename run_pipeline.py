import argparse
import json
from pathlib import Path

import pandas as pd

from src.services.inference.runner import run_pipeline_texts
from src.utils.parser import parse_methods, ALLOWED_METHODS, to_jsonable


def main():
    parser = argparse.ArgumentParser(description="Run the HCPCS inference pipeline.")

    parser.add_argument(
        "--base-dir",
        type=str,
        default=str(Path(__file__).parent),
        help="Base directory for resolving relative paths."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input",
        type=str,
        help="Path to a raw policy text file. Use this OR --input-csv + --row (+ --text-column)."
    )
    group.add_argument(
        "--input-csv",
        type=str,
        help="Path to CSV containing policy text. Requires --row (+ optional --text-column). Mutually exclusive with --input."
    )

    parser.add_argument(
        "--row",
        type=int,
        help="1-based row number in the CSV (excluding header). Required if using --input-csv."
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="cleaned_policy_text",
        help="Column name containing policy text (used with --input-csv)."
    )

    parser.add_argument(
        "--output",
        type=str,
        default="src/tests/outputs/sample_output.json",
        help="Output JSON path (resolved relative to --base-dir if not absolute)."
    )
    parser.add_argument(
        "--methods",
        type=parse_methods,
        default=parse_methods("lexical"),
        help=f"Comma-separated inference methods. Allowed: {ALLOWED_METHODS}. Example: lexical,llm"
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir)

    # Conditional validation for CSV mode
    if args.input_csv is not None and args.row is None:
        parser.error("--input-csv requires --row (and optionally --text-column).")

    # Resolve input source + load policy text(s)
    if args.input is not None:
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = base_dir / input_path

        with open(input_path, "r", encoding="utf-8") as f:
            policy_texts = [f.read()]

        input_display = str(input_path)

    else:  # args.input_csv is not None
        csv_path = Path(args.input_csv)
        if not csv_path.is_absolute():
            csv_path = base_dir / csv_path

        df = pd.read_csv(csv_path)

        idx = args.row - 2  # row=2 => first data row => iloc[0]
        if idx < 0 or idx >= len(df):
            raise ValueError(f"--row {args.row} out of range. Valid: 2..{len(df)+1}")

        if args.text_column not in df.columns:
            raise ValueError(f"Column '{args.text_column}' not found in CSV. Available: {list(df.columns)}")

        policy_texts = [str(df.iloc[idx][args.text_column])]
        input_display = f"{csv_path} (row={args.row}, col={args.text_column})"

    # Resolve output path relative to --base-dir (if needed)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = base_dir / output_path

    # Display config (after resolution so it's accurate)
    print("HCPCS inference pipeline running")
    print(f"Input:  {input_display}")
    print(f"Output: {output_path}")

    # Run the inference pipeline
    result = run_pipeline_texts(policy_texts, args.methods)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the result
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(to_jsonable(result), outfile, indent=4)

    print(f"Inference results saved to {output_path}")


if __name__ == "__main__":
    main()