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
            if text:
                reqs.append(Requirement(section=section, text=text))
            continue

        if re.match(r"^\d+\.\s+", line):
            text = re.sub(r"^\d+\.\s+", "", line)
            reqs.append(Requirement(section=section, text=text))
    return reqs


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
                "requirement": req.text,
                "category": category,
                "test_hint": test_hint,
            }
        )
    return matrix
