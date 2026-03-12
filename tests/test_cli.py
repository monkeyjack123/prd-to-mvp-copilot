from __future__ import annotations

import csv
import json

import pytest

from prd_to_mvp_copilot import cli


def test_cli_validate_with_custom_required_sections_passes(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    prd.write_text("# Problem\n# Scope\n- Must support auth\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "prd-mvp",
            str(prd),
            "--validate",
            "--require-section",
            "Problem",
            "--require-section",
            "Scope",
        ],
    )

    cli.main()
    captured = capsys.readouterr()

    assert "Validation passed." in captured.err
    assert "Problem, Scope" in captured.err


def test_cli_validate_with_custom_required_sections_fails(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    prd.write_text("# Problem\n- Must support auth\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "prd-mvp",
            str(prd),
            "--validate",
            "--require-section",
            "Problem",
            "--require-section",
            "Scope",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "Missing required sections: Scope" in captured.err
    assert "Discovered sections: Problem" in captured.err


def test_cli_fail_on_empty_exits_with_code_2(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    prd.write_text("# Problem\n\nNo bullet requirements here.\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--fail-on-empty"],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "No requirements extracted from PRD" in captured.err


def test_cli_writes_issue_seed_markdown(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "issue-seed.md"
    prd.write_text(
        "# Scope\n- Must support auth\n- Should show dashboard KPI\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--issues-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    content = out.read_text(encoding="utf-8")
    assert "# Generated issue seed" in content
    assert "[HIGH] Must support auth" in content
    assert "### Acceptance Criteria" in content


def test_cli_writes_issue_seed_json(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "issue-seed.json"
    prd.write_text(
        "# Scope\n- Must support auth\n- Should show dashboard KPI\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--issues-json-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    content = out.read_text(encoding="utf-8")
    payload = json.loads(content)
    assert len(payload) == 2
    assert payload[0]["priority"] == "high"
    assert payload[0]["source_requirement_id"] == "REQ-001"


def test_cli_writes_matrix_summary_json(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "matrix-summary.json"
    prd.write_text(
        "# Core\n- Must support auth\n# Dashboard\n- Should show dashboard KPI\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--summary-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_requirements"] == 2
    assert payload["by_priority"] == {"high": 1, "medium": 1, "low": 0}
    assert payload["by_category"] == {"backend": 1, "frontend": 1, "core": 0}


def test_cli_writes_validation_json_pass_case(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "validation.json"
    prd.write_text(
        "# Problem\n# Users\n# Goals\n# Features\n- Must support auth\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--validation-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["is_valid"] is True
    assert payload["missing_sections"] == []
    assert payload["required_sections"] == ["Problem", "Users", "Goals", "Features"]


def test_cli_writes_validation_json_missing_sections(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "validation.json"
    prd.write_text("# Problem\n- Must support auth\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--validation-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["is_valid"] is False
    assert payload["missing_sections"] == ["Users", "Goals", "Features"]
    assert payload["discovered_sections"] == ["Problem"]


def test_cli_writes_matrix_output_json_file(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "matrix.json"
    prd.write_text("# Scope\n- Must support auth\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--matrix-out", str(out)],
    )

    cli.main()
    captured = capsys.readouterr()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["id"] == "REQ-001"
    assert captured.out.strip().startswith("[")


def test_cli_writes_matrix_output_markdown_file(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "matrix.md"
    prd.write_text("# Scope\n- Should show dashboard KPI\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--format", "md", "--matrix-out", str(out)],
    )

    cli.main()
    captured = capsys.readouterr()

    content = out.read_text(encoding="utf-8")
    assert content.startswith("| id | section | milestone")
    assert "REQ-001" in content
    assert captured.out.startswith("| id | section | milestone")


def test_cli_writes_matrix_csv_file(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "matrix.csv"
    prd.write_text("# Scope\n- Must support auth\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--csv-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    with out.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["id"] == "REQ-001"
    assert rows[0]["priority"] == "high"


def test_cli_markdown_output_escapes_pipe_and_newline_characters(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    out = tmp_path / "generated" / "matrix.md"
    prd.write_text("# Scope\n- Must support OAuth | SSO\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--format", "md", "--matrix-out", str(out)],
    )

    cli.main()
    _ = capsys.readouterr()

    content = out.read_text(encoding="utf-8")
    assert "Must support OAuth \\| SSO" in content


def test_cli_dedupe_collapses_duplicate_requirements_within_same_section(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    prd.write_text(
        "# Scope\n- Must support auth\n- must support auth\n# Dashboard\n- Must support auth\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--dedupe"],
    )

    cli.main()
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert len(payload) == 2
    assert payload[0]["section"] == "Scope"
    assert payload[1]["section"] == "Dashboard"


def test_cli_min_priority_filters_matrix_output(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    prd.write_text(
        "# Scope\n- Must support auth\n- Should show dashboard KPI\n- Nice-to-have copy polish\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["prd-mvp", str(prd), "--min-priority", "medium"],
    )

    cli.main()
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert [row["priority"] for row in payload] == ["high", "medium"]


def test_cli_min_priority_filters_issue_seed_and_summary_outputs(tmp_path, capsys, monkeypatch):
    prd = tmp_path / "sample.md"
    issues_out = tmp_path / "generated" / "issue-seed.json"
    summary_out = tmp_path / "generated" / "summary.json"
    prd.write_text(
        "# Scope\n- Must support auth\n- Should show dashboard KPI\n- Nice-to-have copy polish\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "prd-mvp",
            str(prd),
            "--min-priority",
            "high",
            "--issues-json-out",
            str(issues_out),
            "--summary-out",
            str(summary_out),
        ],
    )

    cli.main()
    _ = capsys.readouterr()

    issues_payload = json.loads(issues_out.read_text(encoding="utf-8"))
    summary_payload = json.loads(summary_out.read_text(encoding="utf-8"))

    assert len(issues_payload) == 1
    assert issues_payload[0]["priority"] == "high"
    assert summary_payload["total_requirements"] == 1
    assert summary_payload["by_priority"] == {"high": 1, "medium": 0, "low": 0}
