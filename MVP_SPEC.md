# MVP_SPEC.md

## 1) Goal
Build a 2-week MVP that transforms a PRD markdown file into a runnable **Next.js + FastAPI** scaffold with docs and initial backlog.

## 2) Functional Requirements
1. Accept PRD input path via CLI.
2. Parse key PRD sections into structured model.
3. Generate monorepo scaffold:
   - `apps/frontend` (Next.js)
   - `apps/backend` (FastAPI)
   - `packages/shared` (schemas/types)
4. Generate starter API routes and frontend pages from inferred entities/features.
5. Output architecture and run instructions.
6. Generate initial GitHub issues (first 10).

## 3) Non-Functional Requirements
- Local setup in < 10 minutes on clean machine.
- Reproducible generation from same PRD input.
- Lint/test/build commands available for both services.
- Clear error messages for malformed PRDs.

## 4) Proposed Architecture

```text
                +----------------------+
                |   PRD (.md input)    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | PRD Parser/Extractor |
                |  (sections -> JSON)  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  Scaffold Generator  |
                |  templates + mapper  |
                +----+------------+----+
                     |            |
                     v            v
        +------------------+   +------------------+
        | Next.js Frontend |   | FastAPI Backend  |
        | pages/components |   | routes/services  |
        +---------+--------+   +---------+--------+
                  |                      |
                  +----------+-----------+
                             v
                  +----------------------+
                  | Shared Contracts      |
                  | OpenAPI + TS types    |
                  +----------------------+
```

### Monorepo Structure

```bash
prd-to-mvp-copilot/
  apps/
    frontend/              # Next.js app router scaffold
    backend/               # FastAPI app
  packages/
    shared/                # pydantic/json schema + TS types
  templates/               # generator templates
  scripts/                 # helper scripts
  docs/
    ARCHITECTURE.md
    QUICKSTART.md
  generated/
    issue-seed.md
  prd/                     # input examples
  cli/                     # entrypoint
```

## 5) API + UI Contract Strategy
- Backend exposes `/health` and `/api/v1/<resource>` endpoints.
- OpenAPI schema generated from FastAPI routes.
- Frontend uses generated client (or typed fetch wrapper) from OpenAPI/types.
- Shared types live in `packages/shared` for compile-time consistency.

## 6) CLI Design

### Primary Command
```bash
npx prd-to-mvp-copilot generate --prd ./prd/sample-prd.md --out ./output --name demo-app
```

### Suggested CLI Subcommands
```bash
prd-to-mvp-copilot init
prd-to-mvp-copilot generate --prd <path> --out <path> --name <app-name>
prd-to-mvp-copilot validate --prd <path>
prd-to-mvp-copilot doctor
```

### CLI Behaviors
- `validate`: checks required PRD headings + returns warnings/errors.
- `generate`: creates/overwrites scaffold with summary output.
- `doctor`: verifies Node/Python/pnpm/uv availability.

## 7) Development Commands (Generated Project)

### Prerequisites
- Node 20+
- pnpm 9+
- Python 3.11+
- uv or pip

### Setup
```bash
# from generated project root
pnpm install
cd apps/backend && uv sync && cd ../..
cp .env.example .env
```

### Run
```bash
# terminal 1
pnpm --filter frontend dev

# terminal 2
pnpm --filter backend dev
```

### Build/Test/Lint
```bash
pnpm lint
pnpm test
pnpm build
pnpm --filter backend test
```

## 8) 2-Week Delivery Plan

### Week 1
- **Day 1-2:** PRD schema + parser + validation.
- **Day 3-4:** monorepo templates and generation engine.
- **Day 5:** FastAPI route stubs + health endpoint + OpenAPI export.

### Week 2
- **Day 6-7:** Next.js pages + API client wiring.
- **Day 8:** CLI polish (`validate`, `generate`, `doctor`).
- **Day 9:** docs generation + issue seeding + sample PRD.
- **Day 10:** end-to-end tests, bug fixes, release prep.

## 9) Definition of Done
- CLI can validate and generate scaffold from sample PRD.
- Generated frontend and backend start successfully.
- `/health` endpoint responds 200.
- Frontend successfully fetches one backend resource.
- Docs and issue list are generated and understandable.

## 10) Key Open Questions
1. Should parser be rule-based only in MVP, or include optional LLM assist?
2. Should generation target `pnpm` only, or include npm fallback?
3. Should backend default DB be SQLite or in-memory JSON for speed?
