from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import extract_requirements, build_task_matrix, matrix_json_schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MVP task matrix from PRD markdown")
    parser.add_argument("input", type=Path, help="Path to PRD markdown")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument(
        "--schema-out",
        type=Path,
        help="Optional path to write task matrix JSON Schema",
    )
    args = parser.parse_args()

    prd_text = args.input.read_text(encoding="utf-8")
    matrix = build_task_matrix(extract_requirements(prd_text))

    if args.schema_out:
        args.schema_out.write_text(json.dumps(matrix_json_schema(), indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(matrix, indent=2))
    else:
        print("| id | section | milestone | category | requirement | test_hint |")
        print("|---|---|---|---|---|---|")
        for row in matrix:
            print(
                f"| {row['id']} | {row['section']} | {row['milestone']} | {row['category']} | {row['requirement']} | {row['test_hint']} |"
            )


if __name__ == "__main__":
    main()
