from prd_to_mvp_copilot.parser import extract_requirements, build_task_matrix


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


def test_build_task_matrix_assigns_categories():
    text = """
# Scope
- Implement auth middleware
- Create dashboard UI
- Add billing webhook
"""
    matrix = build_task_matrix(extract_requirements(text))
    assert matrix[0]["category"] == "backend"
    assert matrix[1]["category"] == "frontend"
    assert matrix[2]["category"] == "core"
    assert matrix[0]["id"] == "REQ-001"
