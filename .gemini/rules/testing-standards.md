---
description: Unified testing standards, test-driven development workflow, and multi-tier verification matrix (Unit, Integration, Contract, E2E, Load).
globs: ["tests/**/*", "web/tests/**/*", "**/*.test.*", "**/*.spec.*", "pyproject.toml", "web/package.json"]
---

# Testing Standards & Verification Matrix

Derived from ECC (Enhanced Claude Code) testing patterns and tailored for the Talent Marketplace Engine.

## 1. Core Testing Doctrine

- **Test-Driven Development (TDD)**: All features and bugfixes follow RED -> GREEN -> REFACTOR.
  1. RED: Write failing test expressing desired behavior.
  2. GREEN: Implement minimal viable code to pass.
  3. REFACTOR: Eliminate duplication and improve structure while preserving green tests.
- **Coverage Mandate**: Minimum 80% coverage on backend services and frontend components; 100% coverage on critical paths:
  - Core algorithmic engine (`core/engine/*`)
  - Hybrid scoring mathematics (`core/engine/scoring.py` / `core/engine/dp/*`)
  - Resume parser sanitization & entity extraction
- **AAA Pattern**: All tests must strictly follow Arrange-Act-Assert structure.
- **Behavior-Driven Naming**: Test names must explain behavior and expected outcome (e.g. `test_match_score_zero_division_returns_fallback`).

## 2. Multi-Tier Verification Matrix

### Layer 1: Unit & Algorithmic Tests (`tests/unit/`, `tests/benchmarks/`)
- Test individual data structures, string algorithms, dynamic programming solvers, and network flows in total isolation.
- Verify Big-O scaling empirically: Dinic's $O(V^2 E)$, Aho-Corasick linear scan $O(N + M)$, SOS DP $O(n \cdot 2^n)$.
- Verify boundary conditions: empty candidate pool, zero required experience, 100% duplicate texts, disjoint skill taxonomies.

### Layer 2: Database & Backend Integration Tests (`tests/integration/test_db_integration.py`)
- Framework: `pytest` with `testcontainers-python` spinning up PostgreSQL with `pgvector/pgvector:pg16`.
- Execution: Run Alembic migrations (`alembic upgrade head`), seed reference job requisitions and candidate embeddings, and verify end-to-end vector cosine queries and hybrid scoring against real database state.
- Isolation: Each test session or module runs in an isolated container or transaction rollback.

### Layer 3: API Contract & OpenAPI Fuzzing (`tests/contract/test_openapi.py`)
- Framework: `schemathesis` against FastAPI OpenAPI schema (`http://localhost:8000/openapi.json` or ASGI app).
- Validation: Automatically fuzz all endpoints to confirm schema conformance, HTTP status codes, query parameter constraints, and ensure no unhandled 500 errors or schema drifts occur.

### Layer 4: Frontend Component Tests (`web/tests/components/`)
- Framework: `vitest` + `@testing-library/react` + `@testing-library/user-event` configured via `web/vitest.config.ts`.
- Principles:
  - Query by accessibility roles (`getByRole`, `getByLabelText`) before `data-testid`.
  - Simulate real interactions with `userEvent` (not synthetic `fireEvent`).
  - Use `findBy*` or `waitFor()` for asynchronous state changes.

### Layer 5: End-to-End User Journey Tests (`web/tests/e2e/marketplace.spec.ts`)
- Framework: `playwright` configured via `web/playwright.config.ts`.
- Pattern: Page Object Model (POM) encapsulation for candidate and recruiter portals.
- Journeys:
  1. Candidate Flow: Upload resume -> inspect parsed skills & experience -> view matching jobs with ATS diagnostic feedback.
  2. Recruiter Flow: Create job requisition -> trigger hybrid matching -> view ranked candidate leaderboard.
- Reliability: Strictly use auto-waiting locators and `page.waitForResponse()`; zero arbitrary `waitForTimeout()`. Capture screenshots/traces on failure.

### Layer 6: Performance & Load Testing (`tests/load/k6_match_engine.js`)
- Framework: `k6` concurrency load testing.
- Target: Stress `/api/v1/marketplace/match` with concurrent virtual recruiters.
- SLAs:
  - 95th percentile latency (p95) < 500ms under concurrent VUs.
  - Error rate < 1%.
  - Verify thread pool and connection pool contention under load.

## 3. Standard Verification Commands

```bash
# Backend Unit & Core Tests
uv run pytest tests/unit/ -v

# Backend Integration Tests (with Testcontainers)
uv run pytest tests/integration/test_db_integration.py -v

# API Contract Tests (Schemathesis)
uv run pytest tests/contract/test_openapi.py -v

# Frontend Component Tests (Vitest)
cd web && pnpm run test

# Frontend E2E Tests (Playwright)
cd web && pnpm exec playwright test

# Load Tests (k6)
k6 run tests/load/k6_match_engine.js
```
