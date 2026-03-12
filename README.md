# prd-to-mvp-copilot

Turn product requirements into runnable MVP scaffolds.

## What ships in v0.1
- PRD markdown parser for bullet/numbered requirements (supports `-`/`*`/`+` bullets, `1.`/`1)`/`a)`/`i.` formats, plus GitHub task-list checkboxes)
- Section detection supports both ATX headings (`# Heading`) and Setext headings (`Heading` + `===`/`---`)
- Ignores list-like text inside fenced code blocks (``` / ~~~) so examples/snippets do not pollute extracted requirements
- Task-matrix generator with category + milestone mapping + effort sizing + test hints
- Priority inference (`high`/`medium`/`low`) from requirement language (`must`, `critical`, `should`, etc.)
- CLI (`prd-mvp`) outputting JSON or Markdown table
- Optional matrix file export (`--matrix-out`) in either JSON or Markdown format for CI artifacts
- Optional PRD section validation (`--validate`) with default Problem/Users/Goals/Features, overridable via repeated `--require-section`
- Optional strict extraction guard (`--fail-on-empty`) to fail fast when no actionable requirements were parsed
- Optional JSON Schema export for downstream validators/contracts
- Optional issue-seed markdown generation (`--issues-out`) for fast GitHub backlog drafting
- Optional issue-seed JSON export (`--issues-json-out`) for automation pipelines and API ingestion
- Optional matrix summary JSON export (`--summary-out`) with counts by priority/category/milestone for sprint planning
- Optional validation report JSON export (`--validation-out`) containing required/missing/discovered section data for CI gates
- Demo PRD and pytest coverage

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
prd-mvp demo/sample_prd.md --format md --schema-out demo/task_matrix.schema.json --validate
# custom validation contract (repeat --require-section)
prd-mvp demo/sample_prd.md --validate --require-section Problem --require-section Features
# write matrix output to an artifact file while still printing stdout
prd-mvp demo/sample_prd.md --format md --matrix-out generated/task-matrix.md
# generate issue-seed markdown for backlog import
prd-mvp demo/sample_prd.md --issues-out generated/issue-seed.md
# generate issue-seed JSON for automation
prd-mvp demo/sample_prd.md --issues-json-out generated/issue-seed.json
# export matrix summary for sprint planning and reporting
prd-mvp demo/sample_prd.md --summary-out generated/matrix-summary.json
# export machine-readable validation details for CI checks
prd-mvp demo/sample_prd.md --validation-out generated/validation.json
# fail CI quickly when a PRD has no parsed bullet/numbered requirements
prd-mvp demo/sample_prd.md --fail-on-empty
```

## Example output

```text
| id | section | milestone | category | priority | effort | requirement | test_hint |
|---|---|---|---|---|---|---|---|
| REQ-001 | Core jobs | M1-foundation | backend | high | small | Must support login and reset password | auth flow passes |
| REQ-002 | Core jobs | M1-foundation | frontend | medium | medium | Should show dashboard weekly activation trend | render and interaction snapshot |
| REQ-003 | Core jobs | M1-foundation | core | low | medium | Export account activity CSV | acceptance criteria validated |
```

## Repo structure

- `src/prd_to_mvp_copilot/parser.py` — extraction + matrix logic
- `src/prd_to_mvp_copilot/cli.py` — CLI entrypoint
- `tests/test_parser.py` — unit tests
- `demo/sample_prd.md` — runnable demo input

## Roadmap
- v0.2: output story points + effort estimates
- v0.3: generate scaffold templates per requirement category
