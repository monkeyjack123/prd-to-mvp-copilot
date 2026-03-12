from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class Requirement:
    section: str
    text: str


@dataclass
class PrdValidationResult:
    required_sections: list[str]
    missing_sections: list[str]
    discovered_sections: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.missing_sections


def _normalize_section_name(section: str) -> str:
    return re.sub(r"\s+", " ", section.strip().lower())


def _is_setext_underline(line: str) -> bool:
    return bool(re.match(r"^(=+|-+)$", line.strip()))


def _is_candidate_setext_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False
    if stripped.startswith(("- ", "* ", "+ ")):
        return False
    if re.match(r"^(\d+[\.)]|[a-zA-Z][\.)]|[ivxlcdmIVXLCDM]+[\.)])\s+", stripped):
        return False
    return True


def extract_section_headings(prd_text: str) -> list[str]:
    headings: list[str] = []
    in_fenced_code_block = False
    previous_line = ""

    for raw_line in prd_text.splitlines():
        line = raw_line.strip()
        if line.startswith(("```", "~~~")):
            in_fenced_code_block = not in_fenced_code_block
            previous_line = ""
            continue

        if in_fenced_code_block:
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            if heading:
                headings.append(heading)
            previous_line = line
            continue

        if _is_setext_underline(line) and _is_candidate_setext_heading(previous_line):
            headings.append(previous_line.strip())
            previous_line = ""
            continue

        if line:
            previous_line = line

    return headings


def validate_required_sections(
    prd_text: str,
    required_sections: list[str] | None = None,
) -> PrdValidationResult:
    required = required_sections or ["Problem", "Users", "Goals", "Features"]
    discovered = extract_section_headings(prd_text)
    discovered_normalized = {_normalize_section_name(section) for section in discovered}

    missing = [
        section
        for section in required
        if _normalize_section_name(section) not in discovered_normalized
    ]

    return PrdValidationResult(
        required_sections=required,
        missing_sections=missing,
        discovered_sections=discovered,
    )


def extract_requirements(prd_text: str) -> list[Requirement]:
    section = "General"
    reqs: list[Requirement] = []
    in_fenced_code_block = False
    previous_line = ""

    for raw_line in prd_text.splitlines():
        line = raw_line.strip()
        if line.startswith(("```", "~~~")):
            in_fenced_code_block = not in_fenced_code_block
            previous_line = ""
            continue
        if in_fenced_code_block:
            continue
        if not line:
            previous_line = ""
            continue
        if line.startswith("#"):
            section = line.lstrip("#").strip() or section
            previous_line = line
            continue
        if _is_setext_underline(line) and _is_candidate_setext_heading(previous_line):
            section = previous_line.strip() or section
            previous_line = ""
            continue
        if line.startswith(("- ", "* ", "+ ")):
            text = line[2:].strip()
            text = re.sub(r"^\[[ xX]\]\s*", "", text)
            if text:
                reqs.append(Requirement(section=section, text=text))
            previous_line = line
            continue

        if re.match(r"^(\d+[\.)]|[a-zA-Z][\.)]|[ivxlcdmIVXLCDM]+[\.)])\s+", line):
            text = re.sub(r"^(\d+[\.)]|[a-zA-Z][\.)]|[ivxlcdmIVXLCDM]+[\.)])\s+", "", line)
            reqs.append(Requirement(section=section, text=text))

        previous_line = line

    return reqs


def map_section_to_milestone(section: str, category: str) -> str:
    lower = section.lower()
    if any(token in lower for token in ("auth", "core", "foundation", "account")):
        return "M1-foundation"
    if any(token in lower for token in ("integration", "api", "backend", "data")):
        return "M2-integrations"
    if any(token in lower for token in ("ui", "dashboard", "frontend", "experience")):
        return "M3-experience"

    if category == "backend":
        return "M2-integrations"
    if category == "frontend":
        return "M3-experience"
    return "M1-foundation"


def infer_priority(requirement_text: str) -> str:
    lower = requirement_text.lower()
    if any(token in lower for token in ("must", "critical", "required", "blocker", "p0")):
        return "high"
    if any(token in lower for token in ("should", "important", "p1")):
        return "medium"
    return "low"


def infer_effort(requirement_text: str) -> str:
    lower = requirement_text.lower()
    if any(
        token in lower
        for token in (
            "migrate",
            "multi-tenant",
            "real-time",
            "stream",
            "webhook",
            "integration",
            "oauth",
            "sso",
            "encryption",
            "permissions",
        )
    ):
        return "large"
    if any(
        token in lower
        for token in (
            "dashboard",
            "export",
            "report",
            "search",
            "filter",
            "notification",
            "onboarding",
            "billing",
            "analytics",
        )
    ):
        return "medium"
    return "small"


def build_task_matrix(requirements: list[Requirement]) -> list[dict[str, str]]:
    matrix = []
    for i, req in enumerate(requirements, start=1):
        lower = req.text.lower()
        if "auth" in lower or "login" in lower:
            category = "backend"
            test_hint = "auth flow passes"
        elif "ui" in lower or "dashboard" in lower:
            category = "frontend"
            test_hint = "render and interaction snapshot"
        else:
            category = "core"
            test_hint = "acceptance criteria validated"

        matrix.append(
            {
                "id": f"REQ-{i:03d}",
                "section": req.section,
                "milestone": map_section_to_milestone(req.section, category),
                "requirement": req.text,
                "category": category,
                "priority": infer_priority(req.text),
                "effort": infer_effort(req.text),
                "test_hint": test_hint,
            }
        )
    return matrix


def generate_issue_seed(matrix: list[dict[str, str]]) -> list[dict[str, object]]:
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    issues: list[dict[str, object]] = []

    sorted_matrix = sorted(
        matrix,
        key=lambda row: (
            priority_rank.get(row["priority"], 99),
            row["milestone"],
            row["id"],
        ),
    )

    for row in sorted_matrix:
        issues.append(
            {
                "title": f"[{row['priority'].upper()}] {row['requirement']}",
                "priority": row["priority"],
                "milestone": row["milestone"],
                "category": row["category"],
                "source_requirement_id": row["id"],
                "description": (
                    f"Implement requirement from section '{row['section']}'."
                    f"\n\nRequirement: {row['requirement']}"
                ),
                "acceptance_criteria": [
                    f"Requirement {row['id']} is implemented and demonstrable.",
                    f"Tests cover the primary behavior ({row['test_hint']}).",
                    "Documentation is updated for developer onboarding.",
                ],
            }
        )

    return issues


def summarize_matrix(matrix: list[dict[str, str]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "total_requirements": len(matrix),
        "by_priority": {"high": 0, "medium": 0, "low": 0},
        "by_category": {"backend": 0, "frontend": 0, "core": 0},
        "by_milestone": {},
    }

    by_priority = summary["by_priority"]
    by_category = summary["by_category"]
    by_milestone = summary["by_milestone"]

    for row in matrix:
        priority = row["priority"]
        category = row["category"]
        milestone = row["milestone"]

        if priority in by_priority:
            by_priority[priority] += 1
        if category in by_category:
            by_category[category] += 1
        by_milestone[milestone] = by_milestone.get(milestone, 0) + 1

    return summary


def matrix_json_schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PRD to MVP task matrix",
        "type": "array",
        "items": {
            "type": "object",
            "required": [
                "id",
                "section",
                "milestone",
                "requirement",
                "category",
                "priority",
                "effort",
                "test_hint",
            ],
            "properties": {
                "id": {"type": "string", "pattern": "^REQ-\\d{3}$"},
                "section": {"type": "string", "minLength": 1},
                "milestone": {"type": "string", "pattern": "^M[1-3]-"},
                "requirement": {"type": "string", "minLength": 1},
                "category": {"type": "string", "enum": ["backend", "frontend", "core"]},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "effort": {"type": "string", "enum": ["small", "medium", "large"]},
                "test_hint": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    }
