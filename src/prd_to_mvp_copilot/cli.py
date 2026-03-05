from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import extract_requirements, build_task_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MVP task matrix from PRD markdown")
    parser.add_argument("input", type=Path, help="Path to PRD markdown")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()

    prd_text = args.input.read_text(encoding="utf-8")
    matrix = build_task_matrix(extract_requirements(prd_text))

    if args.format == "json":
        print(json.dumps(matrix, indent=2))
    else:
        print("| id | section | category | requirement | test_hint |")
        print("|---|---|---|---|---|")
        for row in matrix:
            print(
                f"| {row['id']} | {row['section']} | {row['category']} | {row['requirement']} | {row['test_hint']} |"
            )


if __name__ == "__main__":
    main()
