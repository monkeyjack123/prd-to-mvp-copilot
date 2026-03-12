import json

from prd_to_mvp_copilot.parser import (
    extract_requirements,
    build_task_matrix,
    map_section_to_milestone,
    matrix_json_schema,
    infer_priority,
    infer_effort,
    extract_section_headings,
    generate_issue_seed,
    summarize_matrix,
    validate_required_sections,
    dedupe_requirements,
)


def test_extract_requirements_reads_bullets_and_numbered_items():
    text = """
# Scope
- User can login with email
* Dashboard shows KPI cards
+ Include SSO login option
1. Export CSV report
2) Send report by email
a) Include weekly digest mode
i. Include audit event trail
"""
    reqs = extract_requirements(text)
    assert [r.text for r in reqs] == [
        "User can login with email",
        "Dashboard shows KPI cards",
        "Include SSO login option",
        "Export CSV report",
        "Send report by email",
        "Include weekly digest mode",
        "Include audit event trail",
    ]


def test_extract_requirements_normalizes_task_list_checkboxes():
    text = """
# Scope
- [ ] Must support GitHub task lists
- [x] Should keep completed items parseable
"""
    reqs = extract_requirements(text)
    assert [r.text for r in reqs] == [
        "Must support GitHub task lists",
        "Should keep completed items parseable",
    ]


def test_extract_requirements_skips_fenced_code_blocks():
    text = """
# Scope
- Parse this requirement
```markdown
- do not parse this code bullet
1. do not parse this code item
```
2. Parse this numbered item
"""
    reqs = extract_requirements(text)
    assert [r.text for r in reqs] == [
        "Parse this requirement",
        "Parse this numbered item",
    ]


def test_build_task_matrix_assigns_categories_milestones_and_priority():
    text = """
# Core jobs
- Must implement auth middleware
# Dashboard
- Should create dashboard UI
# Misc
- Add billing webhook
"""
    matrix = build_task_matrix(extract_requirements(text))
    assert matrix[0]["category"] == "backend"
    assert matrix[1]["category"] == "frontend"
    assert matrix[2]["category"] == "backend"
    assert matrix[0]["milestone"] == "M1-foundation"
    assert matrix[1]["milestone"] == "M3-experience"
    assert matrix[2]["milestone"] == "M2-integrations"
    assert matrix[0]["id"] == "REQ-001"
    assert matrix[0]["priority"] == "high"
    assert matrix[1]["priority"] == "medium"
    assert matrix[2]["priority"] == "low"
    assert matrix[0]["effort"] == "small"
    assert matrix[1]["effort"] == "medium"
    assert matrix[2]["effort"] == "large"


def test_map_section_to_milestone_uses_section_and_category_fallbacks():
    assert map_section_to_milestone("API Integrations", "core") == "M2-integrations"
    assert map_section_to_milestone("Random", "frontend") == "M3-experience"


def test_infer_priority_with_keywords_and_default():
    assert infer_priority("Critical: support migration") == "high"
    assert infer_priority("Should support export") == "medium"
    assert infer_priority("Polish onboarding copy") == "low"


def test_infer_effort_with_keywords_and_default():
    assert infer_effort("Implement OAuth SSO integration") == "large"
    assert infer_effort("Create analytics dashboard") == "medium"
    assert infer_effort("Fix typo in docs") == "small"


def test_extract_section_headings_skips_code_block_headings():
    text = """
# Problem
~~~md
# Not a real section heading
~~~
## Users
### Features
"""
    assert extract_section_headings(text) == ["Problem", "Users", "Features"]


def test_extract_section_headings_supports_setext_style_headings():
    text = """
Problem Statement
=================

Users
-----

- Must support SSO
"""
    assert extract_section_headings(text) == ["Problem Statement", "Users"]


def test_extract_requirements_uses_setext_headings_for_section_context():
    text = """
Scope
=====
- Must support auth middleware

Dashboard
---------
- Should show weekly KPIs
"""
    reqs = extract_requirements(text)
    assert [(r.section, r.text) for r in reqs] == [
        ("Scope", "Must support auth middleware"),
        ("Dashboard", "Should show weekly KPIs"),
    ]


def test_validate_required_sections_is_case_insensitive():
    text = """
# problem
# USERS
# Goals
# Features
"""
    result = validate_required_sections(text)
    assert result.is_valid is True
    assert result.missing_sections == []


def test_validate_required_sections_reports_missing():
    text = """
# Problem
# Users
"""
    result = validate_required_sections(text)
    assert result.is_valid is False
    assert result.missing_sections == ["Goals", "Features"]


def test_generate_issue_seed_sorts_by_priority_and_keeps_requirement_links():
    text = """
# Core
- Should add weekly dashboard
- Must support auth middleware
"""
    matrix = build_task_matrix(extract_requirements(text))
    issues = generate_issue_seed(matrix)

    assert issues[0]["priority"] == "high"
    assert issues[0]["source_requirement_id"] == "REQ-002"
    assert "Acceptance Criteria" not in issues[0]  # criteria is structured list
    assert len(issues[0]["acceptance_criteria"]) == 3


def test_summarize_matrix_returns_priority_category_and_milestone_counts():
    text = """
# Core
- Must support auth middleware
# Dashboard
- Should show dashboard weekly trend
# API
- Add analytics export endpoint
"""
    matrix = build_task_matrix(extract_requirements(text))
    summary = summarize_matrix(matrix)

    assert summary["total_requirements"] == 3
    assert summary["by_priority"] == {"high": 1, "medium": 1, "low": 1}
    assert summary["by_category"] == {"backend": 2, "frontend": 1, "core": 0}
    assert summary["by_milestone"]["M1-foundation"] == 1
    assert summary["by_milestone"]["M2-integrations"] == 1
    assert summary["by_milestone"]["M3-experience"] == 1


def test_matrix_json_schema_contract_has_required_fields():
    schema = matrix_json_schema()
    items = schema["items"]
    assert schema["type"] == "array"
    assert "milestone" in items["required"]
    assert "priority" in items["required"]
    assert "effort" in items["required"]
    assert items["properties"]["category"]["enum"] == ["backend", "frontend", "core"]
    assert items["properties"]["priority"]["enum"] == ["high", "medium", "low"]
    assert items["properties"]["effort"]["enum"] == ["small", "medium", "large"]
    assert items["additionalProperties"] is False

    json.dumps(schema)

def test_extract_section_headings_trims_closing_atx_hashes():
    text = """
# Problem #
## Users ####
### Features
"""
    assert extract_section_headings(text) == ["Problem", "Users", "Features"]


def test_extract_requirements_uses_trimmed_atx_section_name_context():
    text = """
## Dashboard ####
- Should show weekly KPIs
"""
    reqs = extract_requirements(text)
    assert [(r.section, r.text) for r in reqs] == [
        ("Dashboard", "Should show weekly KPIs"),
    ]


def test_dedupe_requirements_drops_section_local_duplicates_case_insensitively():
    text = """
# Scope
- Must support auth
- must support   auth
# Dashboard
- Must support auth
"""
    reqs = extract_requirements(text)
    deduped = dedupe_requirements(reqs)

    assert [(r.section, r.text) for r in deduped] == [
        ("Scope", "Must support auth"),
        ("Dashboard", "Must support auth"),
    ]
