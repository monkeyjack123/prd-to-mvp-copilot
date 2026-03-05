# prd-to-mvp-copilot

Turn product requirements into runnable MVP scaffolds.

## What ships in v0.1
- PRD markdown parser for bullet/numbered requirements (supports `1.`/`1)`/`a)` formats, plus GitHub task-list checkboxes)
- Task-matrix generator with category + milestone mapping + test hints
- Priority inference (`high`/`medium`/`low`) from requirement language (`must`, `critical`, `should`, etc.)
- CLI (`prd-mvp`) outputting JSON or Markdown table
- Optional JSON Schema export for downstream validators/contracts
- Demo PRD and pytest coverage

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
prd-mvp demo/sample_prd.md --format md --schema-out demo/task_matrix.schema.json
```

## Example output

```text
| id | section | milestone | category | priority | requirement | test_hint |
|---|---|---|---|---|---|---|
| REQ-001 | Core jobs | M1-foundation | backend | high | Must support login and reset password | auth flow passes |
| REQ-002 | Core jobs | M1-foundation | frontend | medium | Should show dashboard weekly activation trend | render and interaction snapshot |
| REQ-003 | Core jobs | M1-foundation | core | low | Export account activity CSV | acceptance criteria validated |
```

## Repo structure

- `src/prd_to_mvp_copilot/parser.py` — extraction + matrix logic
- `src/prd_to_mvp_copilot/cli.py` — CLI entrypoint
- `tests/test_parser.py` — unit tests
- `demo/sample_prd.md` — runnable demo input

## Roadmap
- v0.2: output story points + effort estimates
- v0.3: generate scaffold templates per requirement category
