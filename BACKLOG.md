# BACKLOG.md

## Sprint Window
**Duration:** 2 weeks (10 working days)  
**Objective:** Ship v0.1 MVP that generates runnable Next.js + FastAPI scaffold from PRD markdown.

## Prioritization Legend
- **P0**: must-have for MVP
- **P1**: should-have for MVP completeness
- **P2**: nice-to-have (defer if needed)

---

## First 10 GitHub Issues (Seed)

### 1) [P0] Define PRD Input Schema + Required Sections
**Type:** Feature  
**Description:** Define minimal PRD contract and parser expectations.

**Acceptance Criteria:**
- Document required headings (e.g., Problem, Users, Goals, Features).
- Add JSON schema or equivalent validation rules.
- Include one valid and one invalid PRD sample in `prd/examples/`.
- README documents expected PRD format.

---

### 2) [P0] Implement PRD Parser and Normalized Output Model
**Type:** Feature  
**Description:** Parse markdown PRD into normalized machine-readable structure.

**Acceptance Criteria:**
- Parser outputs stable JSON shape (versioned).
- Handles missing optional sections gracefully.
- Emits warnings for ambiguous/missing critical fields.
- Unit tests cover at least 5 PRD parsing scenarios.

---

### 3) [P0] Scaffold Monorepo Template (Next.js + FastAPI + Shared)
**Type:** Feature  
**Description:** Build template folder and generation pipeline for target monorepo.

**Acceptance Criteria:**
- Generated directories: `apps/frontend`, `apps/backend`, `packages/shared`.
- Root scripts for install/lint/test/build are present.
- `.env.example` and `.gitignore` included.
- Running generation twice does not produce broken structure.

---

### 4) [P0] Build CLI Entrypoint (`generate`, `validate`, `doctor`)
**Type:** Feature  
**Description:** Implement command surface for main workflows.

**Acceptance Criteria:**
- `generate --prd --out --name` works end-to-end.
- `validate --prd` returns pass/fail + actionable messages.
- `doctor` checks required runtime dependencies.
- `--help` is available for all commands.

---

### 5) [P0] Generate FastAPI Starter with Health + Resource Routes
**Type:** Feature  
**Description:** Create backend app with baseline route stubs inferred from PRD features/entities.

**Acceptance Criteria:**
- `/health` endpoint returns 200 with status payload.
- At least one generated CRUD-like route group under `/api/v1`.
- App boots with `uvicorn` from generated scripts.
- OpenAPI docs available at `/docs`.

---

### 6) [P0] Generate Next.js Starter Pages + API Integration
**Type:** Feature  
**Description:** Create frontend pages and wire to backend endpoint(s).

**Acceptance Criteria:**
- Landing page includes project summary from PRD metadata.
- At least one generated list/detail view based on resource.
- Frontend can call backend API using generated client/wrapper.
- `pnpm --filter frontend dev` starts without manual fixes.

---

### 7) [P1] Shared Type Contracts (OpenAPI/Schema -> TS/Python)
**Type:** Feature  
**Description:** Ensure contract consistency between backend and frontend.

**Acceptance Criteria:**
- Shared schema artifacts stored in `packages/shared`.
- Frontend uses typed models for one core resource.
- Contract generation command documented.
- Contract drift check added to CI or local script.

---

### 8) [P1] Quickstart + Architecture Docs Generation
**Type:** Documentation  
**Description:** Auto-generate docs in output project for quick onboarding.

**Acceptance Criteria:**
- `docs/QUICKSTART.md` includes prerequisites + setup/run commands.
- `docs/ARCHITECTURE.md` includes component diagram and data flow.
- Troubleshooting section for top 3 setup issues.
- Docs are referenced from root README.

---

### 9) [P1] End-to-End Smoke Test for Generated Project
**Type:** Quality  
**Description:** Add automated test to validate generated scaffold is runnable.

**Acceptance Criteria:**
- CI/local script generates project from sample PRD.
- Script runs backend and validates `/health` response.
- Script runs frontend build successfully.
- Failing smoke test blocks release tag.

---

### 10) [P1] Seed Backlog Generator (Issue Draft Output)
**Type:** Feature  
**Description:** Emit first-pass issue list tailored to parsed PRD.

**Acceptance Criteria:**
- Output includes at least 10 issue drafts with titles and descriptions.
- Each issue includes acceptance criteria section.
- Issues are grouped by priority/milestone.
- Generated issue file saved as `generated/issue-seed.md`.

---

## Suggested Milestones
- **Milestone 1 (End Week 1):** Issues #1–#5 complete.
- **Milestone 2 (End Week 2):** Issues #6–#10 complete + smoke test green.

## Dependencies
- #2 depends on #1
- #3 depends on #2
- #4 can begin in parallel with #2/#3
- #6 depends on #5
- #7 depends on #5/#6
- #9 depends on #3/#5/#6
- #10 depends on #2

## Stretch (If Time Remains)
- PRD diff mode (`generate --update`) for iterative regeneration.
- Optional Docker Compose setup for one-command run.
- Template theming (SaaS, marketplace, internal tool presets).
