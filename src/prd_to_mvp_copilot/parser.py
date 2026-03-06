from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class Requirement:
    section: str
    text: str


def extract_requirements(prd_text: str) -> list[Requirement]:
    section = "General"
    reqs: list[Requirement] = []
    for raw_line in prd_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            section = line.lstrip("#").strip() or section
            continue
        if line.startswith(("- ", "* ")):
            text = line[2:].strip()
            text = re.sub(r"^\[[ xX]\]\s*", "", text)
            if text:
                reqs.append(Requirement(section=section, text=text))
            continue

        if re.match(r"^(\d+[\.)]|[a-zA-Z][\.)])\s+", line):
            text = re.sub(r"^(\d+[\.)]|[a-zA-Z][\.)])\s+", "", line)
            reqs.append(Requirement(section=section, text=text))
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
