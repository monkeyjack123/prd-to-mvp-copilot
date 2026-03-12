from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import (
    extract_requirements,
    build_task_matrix,
    generate_issue_seed,
    matrix_json_schema,
    validate_required_sections,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MVP task matrix from PRD markdown")
    parser.add_argument("input", type=Path, help="Path to PRD markdown")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument(
        "--schema-out",
        type=Path,
        help="Optional path to write task matrix JSON Schema",
    )
    parser.add_argument(
        "--issues-out",
        type=Path,
        help="Optional path to write generated issue seed markdown",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate required PRD sections (Problem, Users, Goals, Features)",
    )
    parser.add_argument(
        "--require-section",
        action="append",
        default=[],
        metavar="SECTION",
        help=(
            "Override default required sections for validation. "
            "Repeat flag to require multiple sections."
        ),
    )
    args = parser.parse_args()

    prd_text = args.input.read_text(encoding="utf-8")
    required_sections = args.require_section or None
    validation = validate_required_sections(prd_text, required_sections=required_sections)
    matrix = build_task_matrix(extract_requirements(prd_text))

    if args.schema_out:
        args.schema_out.write_text(json.dumps(matrix_json_schema(), indent=2) + "\n", encoding="utf-8")

    if args.issues_out:
        issues = generate_issue_seed(matrix)
        lines = ["# Generated issue seed", ""]
        for i, issue in enumerate(issues, start=1):
            lines.extend(
                [
                    f"## {i}) {issue['title']}",
                    f"- Priority: {issue['priority']}",
                    f"- Milestone: {issue['milestone']}",
                    f"- Category: {issue['category']}",
                    f"- Source Requirement: {issue['source_requirement_id']}",
                    "",
                    issue["description"],
                    "",
                    "### Acceptance Criteria",
                ]
            )
            for criterion in issue["acceptance_criteria"]:
                lines.append(f"- {criterion}")
            lines.append("")
        args.issues_out.parent.mkdir(parents=True, exist_ok=True)
        args.issues_out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    if args.validate:
        if validation.missing_sections:
            discovered = ", ".join(validation.discovered_sections) or "(none)"
            print(
                "Validation failed. Missing required sections: "
                + ", ".join(validation.missing_sections)
                + ". Discovered sections: "
                + discovered,
                file=sys.stderr,
            )
            sys.exit(2)
        print(
            "Validation passed. Required sections found: "
            + ", ".join(validation.required_sections),
            file=sys.stderr,
        )

    if args.format == "json":
        print(json.dumps(matrix, indent=2))
    else:
        print("| id | section | milestone | category | priority | effort | requirement | test_hint |")
        print("|---|---|---|---|---|---|---|---|")
        for row in matrix:
            print(
                f"| {row['id']} | {row['section']} | {row['milestone']} | {row['category']} | {row['priority']} | {row['effort']} | {row['requirement']} | {row['test_hint']} |"
            )


if __name__ == "__main__":
    main()
