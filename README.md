# prd-to-mvp-copilot

Turn product requirements into runnable MVP scaffolds.

## What ships in v0.1
- PRD markdown parser for bullet/numbered requirements
- Task-matrix generator with category + test hints
- CLI (`prd-mvp`) outputting JSON or Markdown table
- Demo PRD and pytest coverage

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
prd-mvp demo/sample_prd.md --format md
```

## Example output

```text
| id | section | category | requirement | test_hint |
|---|---|---|---|---|
| REQ-001 | Core jobs | backend | User can login and reset password | auth flow passes |
| REQ-002 | Core jobs | frontend | Dashboard UI shows weekly activation trend | render and interaction snapshot |
| REQ-003 | Core jobs | core | Export account activity CSV | acceptance criteria validated |
```

## Repo structure

- `src/prd_to_mvp_copilot/parser.py` — extraction + matrix logic
- `src/prd_to_mvp_copilot/cli.py` — CLI entrypoint
- `tests/test_parser.py` — unit tests
- `demo/sample_prd.md` — runnable demo input

## Roadmap
- v0.2: output story points + effort estimates
- v0.3: generate scaffold templates per requirement category
