# PRODUCT_BRIEF.md

## Product Name
**PRD → MVP Copilot**

## One-line Summary
Convert a lightweight Product Requirements Document (PRD) into a runnable full-stack MVP scaffold (Next.js frontend + FastAPI backend) in minutes.

## Problem
Early-stage builders lose days moving from a PRD to first runnable code. Typical pain points:
- unclear feature slicing for MVP
- inconsistent boilerplate setup across frontend/backend
- no shared contract between UI and API
- delayed first demo due to setup overhead

## Target Users
1. **Solo founders** who need fast validation.
2. **Product engineers** starting greenfield projects.
3. **Small product teams** that need repeatable kickoff scaffolding.

## Jobs To Be Done
- “When I have a PRD, help me generate a working codebase so I can demo quickly.”
- “Give me sane defaults for architecture and dev tooling without yak-shaving.”
- “Provide a backlog I can execute immediately.”

## MVP Value Proposition
In one command, generate:
1. structured feature interpretation of the PRD,
2. Next.js + FastAPI scaffold,
3. API contract and stubs,
4. setup scripts/docs,
5. actionable initial issue backlog.

## Success Criteria (2-week MVP)
- User can run a CLI command against a PRD markdown file.
- Tool outputs a runnable monorepo scaffold.
- `frontend` and `backend` boot successfully with default demo route.
- Generated docs include architecture + quickstart + next issues.
- Time-to-first-demo under **30 minutes** for a new user.

## Non-Goals (MVP)
- production-grade auth/permissions
- multi-cloud deployment automation
- advanced AI planning with long feedback loops
- full PRD semantic validation engine

## Core User Flow
1. User provides `prd.md`.
2. CLI parses key sections (problem, users, goals, features).
3. Generator maps features to basic domain model + API endpoints + pages.
4. Project scaffold is created with runnable services.
5. User starts app via documented commands and sees generated starter app.

## MVP Scope
### In Scope
- PRD ingestion from markdown
- opinionated Next.js + FastAPI template generation
- OpenAPI stub generation from inferred resources
- starter pages + API client wiring
- local dev scripts + documentation
- first-pass backlog generation

### Out of Scope
- custom design systems
- auth providers and billing integrations
- multi-tenant data architecture
- plugin marketplace

## Risks & Mitigations
- **Risk:** PRD ambiguity leads to poor scaffolds.  
  **Mitigation:** required PRD template + fallback defaults + warnings.
- **Risk:** generated code compiles but lacks coherence.  
  **Mitigation:** enforce shared contract and health-check script.
- **Risk:** setup friction across environments.  
  **Mitigation:** include `.env.example`, pinned versions, and Makefile tasks.

## Primary KPI
- **Activation Rate:** % of users who generate scaffold and run both services successfully.

## Secondary KPIs
- Median time from PRD upload to first successful run.
- Number of manual fixes needed before first run.
- % of generated backlogs accepted without major edits.

## Release Definition (v0.1)
MVP is complete when a user can:
1. run the generator on a valid PRD,
2. start frontend/backend locally,
3. hit at least one generated API route from the UI,
4. follow docs without external guidance.
