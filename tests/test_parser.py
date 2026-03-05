import json

from prd_to_mvp_copilot.parser import (
    extract_requirements,
    build_task_matrix,
    map_section_to_milestone,
    matrix_json_schema,
)


def test_extract_requirements_reads_bullets_and_numbered_items():
    text = """
# Scope
- User can login with email
- Dashboard shows KPI cards
1. Export CSV report
"""
    reqs = extract_requirements(text)
    assert [r.text for r in reqs] == [
        "User can login with email",
        "Dashboard shows KPI cards",
        "Export CSV report",
    ]


def test_build_task_matrix_assigns_categories_and_milestones():
    text = """
# Core jobs
- Implement auth middleware
# Dashboard
- Create dashboard UI
# Misc
- Add billing webhook
"""
    matrix = build_task_matrix(extract_requirements(text))
    assert matrix[0]["category"] == "backend"
    assert matrix[1]["category"] == "frontend"
    assert matrix[2]["category"] == "core"
    assert matrix[0]["milestone"] == "M1-foundation"
    assert matrix[1]["milestone"] == "M3-experience"
    assert matrix[2]["milestone"] == "M1-foundation"
    assert matrix[0]["id"] == "REQ-001"


def test_map_section_to_milestone_uses_section_and_category_fallbacks():
    assert map_section_to_milestone("API Integrations", "core") == "M2-integrations"
    assert map_section_to_milestone("Random", "frontend") == "M3-experience"


def test_matrix_json_schema_contract_has_required_fields():
    schema = matrix_json_schema()
    items = schema["items"]
    assert schema["type"] == "array"
    assert "milestone" in items["required"]
    assert items["properties"]["category"]["enum"] == ["backend", "frontend", "core"]
    assert items["additionalProperties"] is False

    json.dumps(schema)
