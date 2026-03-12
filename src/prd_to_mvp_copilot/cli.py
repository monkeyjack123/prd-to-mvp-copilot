from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .parser import (
    extract_requirements,
    dedupe_requirements,
    build_task_matrix,
    generate_issue_seed,
    matrix_json_schema,
    summarize_matrix,
    validate_required_sections,
)


def _escape_markdown_table_cell(value: object) -> str:
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MVP task matrix from PRD markdown")
    parser.add_argument("input", type=Path, help="Path to PRD markdown")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument(
        "--matrix-out",
        type=Path,
        help="Optional path to write task matrix output in selected --format",
    )
    parser.add_argument(
        "--schema-out",
        type=Path,
        help="Optional path to write task matrix JSON Schema",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        help="Optional path to write task matrix as CSV",
    )
    parser.add_argument(
        "--issues-out",
        type=Path,
        help="Optional path to write generated issue seed markdown",
    )
    parser.add_argument(
        "--issues-json-out",
        type=Path,
        help="Optional path to write generated issue seed JSON",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        help="Optional path to write matrix summary JSON (counts by priority/category/milestone)",
    )
    parser.add_argument(
        "--validation-out",
        type=Path,
        help=(
            "Optional path to write PRD section validation JSON "
            "(required/missing/discovered/is_valid)"
        ),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate required PRD sections (Problem, Users, Goals, Features)",
    )
    parser.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="Exit with code 2 when no requirements are extracted from the PRD",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Deduplicate repeated requirements within the same section before matrix generation",
    )
    parser.add_argument(
        "--min-priority",
        choices=["low", "medium", "high"],
        help=(
            "Filter matrix/issue/summary outputs to requirements at or above this priority "
            "(high only, medium+high, or all)."
        ),
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
    requirements = extract_requirements(prd_text)
    if args.dedupe:
        requirements = dedupe_requirements(requirements)
    matrix = build_task_matrix(requirements)

    if args.min_priority:
        priority_rank = {"low": 0, "medium": 1, "high": 2}
        min_rank = priority_rank[args.min_priority]
        matrix = [
            row
            for row in matrix
            if priority_rank.get(row["priority"], -1) >= min_rank
        ]

    if args.fail_on_empty and not matrix:
        print(
            "No requirements extracted from PRD. Add bullet/numbered requirements or remove --fail-on-empty.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.csv_out:
        args.csv_out.parent.mkdir(parents=True, exist_ok=True)
        with args.csv_out.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    "id",
                    "section",
                    "milestone",
                    "category",
                    "priority",
                    "effort",
                    "requirement",
                    "test_hint",
                ],
            )
            writer.writeheader()
            writer.writerows(matrix)

    if args.schema_out:
        args.schema_out.write_text(json.dumps(matrix_json_schema(), indent=2) + "\n", encoding="utf-8")

    issues = generate_issue_seed(matrix)

    if args.issues_out:
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

    if args.issues_json_out:
        args.issues_json_out.parent.mkdir(parents=True, exist_ok=True)
        args.issues_json_out.write_text(json.dumps(issues, indent=2) + "\n", encoding="utf-8")

    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summarize_matrix(matrix), indent=2) + "\n", encoding="utf-8")

    if args.validation_out:
        args.validation_out.parent.mkdir(parents=True, exist_ok=True)
        args.validation_out.write_text(
            json.dumps(
                {
                    "required_sections": validation.required_sections,
                    "missing_sections": validation.missing_sections,
                    "discovered_sections": validation.discovered_sections,
                    "is_valid": validation.is_valid,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

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
        rendered_output = json.dumps(matrix, indent=2)
    else:
        lines = [
            "| id | section | milestone | category | priority | effort | requirement | test_hint |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for row in matrix:
            cells = [
                _escape_markdown_table_cell(row["id"]),
                _escape_markdown_table_cell(row["section"]),
                _escape_markdown_table_cell(row["milestone"]),
                _escape_markdown_table_cell(row["category"]),
                _escape_markdown_table_cell(row["priority"]),
                _escape_markdown_table_cell(row["effort"]),
                _escape_markdown_table_cell(row["requirement"]),
                _escape_markdown_table_cell(row["test_hint"]),
            ]
            lines.append("| " + " | ".join(cells) + " |")
        rendered_output = "\n".join(lines)

    if args.matrix_out:
        args.matrix_out.parent.mkdir(parents=True, exist_ok=True)
        args.matrix_out.write_text(rendered_output + "\n", encoding="utf-8")

    print(rendered_output)


if __name__ == "__main__":
    main()
