# Agent Instructions

## General Rules
*   **FastAPI is the authoritative application API.** Next.js must not duplicate backend business logic.
*   **Reference implementations are forbidden** as substitutes for testing the real application. Tests may use isolated fixtures/mocks only when they are intentionally testing a dependency boundary.
*   **A green test suite is not sufficient** if the tests are testing a mock/reference implementation instead of production code paths.
*   **No fake data in production endpoints.** All endpoints must process real business logic backed by the actual database/algorithms.
*   **No silent fallbacks.** If a service is unavailable, fail loudly so the caller is aware. Do not swallow exceptions and return empty lists or `None` without propagating the error semantics.

## Architecture
- **Backend:** FastAPI, Python 3.12, SQLAlchemy, Alembic, PostgreSQL with pgvector.
- **Frontend:** Next.js 14, React, Tailwind CSS, pnpm. Proxy API requests to backend (`/api/v1/`).
- **Data Models:** Resumes, Jobs, Candidates, CandidateSkills, and JobSkillRequirements.

## Workflow
1.  Verify the task and audit the codebase.
2.  Do NOT invent endpoints; adhere to OpenAPI contracts (`/api/v1/...`).
3.  Implement features.
4.  Run all validation tools before committing.

## Validation & Pre-Commit Steps
```bash
# Python
uv run ruff check . --fix
uv run ruff format .
uv run mypy --explicit-package-bases .
uv run pytest tests/

# Node
cd web
pnpm lint
pnpm typecheck
pnpm test
pnpm exec playwright test
pnpm build
```
