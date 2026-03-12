from __future__ import annotations

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
