# Project: Awesome Dev Pipeline Verification Matrix & Security Gates

## Architecture
The project establishes a comprehensive multi-tier testing, security, and verification matrix for the Resume & Job Matching Talent Marketplace Engine:
- **Rules Tier**: ECC-derived testing standards and security policies in `.gemini/rules/`.
- **Backend Verification Tier**: Testcontainers PostgreSQL (pgvector:pg16) integration tests + Schemathesis OpenAPI contract fuzzing + Alembic schema migrations + WDAC-resilient embedding service.
- **Frontend Verification Tier**: Next.js Vitest component testing + Playwright end-to-end user journeys in `web/`.
- **Performance Tier**: k6 concurrency and latency (p95 < 500ms) load testing against `/api/v1/marketplace/match`.
- **Security & Supply Chain Tier**: Semgrep SAST (`semgrep.yml`), Gitleaks secret detection, Trivy filesystem CVE scanning, and Ponytail-minimal GitHub Actions CI (`.github/workflows/ci.yml`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | ECC Testing & Security Rules | Extract testing standards and security policies from `scratch/ecc-repo` into `.gemini/rules/` | M1 | R1 |
| 2 | Semgrep Security Policy | Custom SAST rules (`semgrep.yml`) enforcing CORS, SQL, secrets, timeouts, zero-stdlib core | M1 | R5 |
| 3 | CI Security & Test Gates | GitHub Actions workflow with gitleaks, semgrep ci, trivy fs ., and test runners | M1 | R5 |
| 4 | Backend Dependencies | Update `pyproject.toml` with `testcontainers[postgres]`, `schemathesis`, `locust`, `httpx` | M2 | R2 |
| 5 | Embedding & Matcher Hardening | WDAC fallback in `core/scoring/embeddings.py` and import fixes in `api/controllers/match.py` | M2 | R2 |
| 6 | Alembic Initial Schema | Create `migrations/versions/20260930_0001_initial_schema.py` with pgvector extension | M2 | R2 |
| 7 | Testcontainers DB Integration | Implement `tests/integration/test_db_integration.py` with pgvector and hybrid scoring | M2 | R2 |
| 8 | Schemathesis Contract Tests | Implement `tests/contract/test_openapi.py` with in-process ASGI contract fuzzing | M2 | R2 |
| 9 | Frontend Test Tooling & Config | `web/package.json` test scripts & devDeps, `web/vitest.config.ts` path alias | M3 | R3 |
| 10 | Frontend Component Tests | Component tests in `web/tests/components/` verifying UI without syntax errors | M3 | R3 |
| 11 | Frontend Playwright E2E | `web/playwright.config.ts` and `web/tests/e2e/marketplace.spec.ts` | M3 | R3 |
| 12 | Marketplace Match Endpoint | Implement `@router.post("/match")` in `api/controllers/marketplace.py` | M4 | R4 |
| 13 | k6 Concurrency Load Test | Implement `tests/load/k6_match_engine.js` measuring p95 latency and HTTP 200 checks | M4 | R4 |
| 14 | Full Pipeline Acceptance Gate | Full multi-tier verification passing all 6 acceptance criteria with clean audit | M5 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Rules & Security Foundation | F1, F2, F3 (`.gemini/rules/*`, `semgrep.yml`, `.github/workflows/ci.yml`) | none | DONE |
| 2 | Backend Verification Matrix | F4, F5, F6, F7, F8 (`pyproject.toml`, `embeddings.py`, `match.py`, migrations, `test_db_integration.py`, `test_openapi.py`) | M1 | IN_PROGRESS |
| 3 | Frontend Verification Matrix | F9, F10, F11 (`web/package.json`, `web/vitest.config.ts`, component tests, playwright config & spec) | M1 | DONE |
| 4 | Marketplace Load Testing | F12, F13 (`api/controllers/marketplace.py`, `tests/load/k6_match_engine.js`) | M2 | DONE |
| 5 | Full Acceptance Verification & Gate | F14 (Run all checks, Reviewer, Challenger, and Forensic Auditor verification) | M1, M2, M3, M4 | PLANNED |

## Interface Contracts
### Marketplace Match Endpoint
- `POST /api/v1/marketplace/match`
- Request: `RecruiterMatchRequest(job_id: str | None, title: str, required_skills: list[str], min_experience: int, candidate_limit: int)`
- Response: `RecruiterMatchResponse(status: str, job_id: str | None, total_candidates: int, matches: list[dict])`

### Database & pgvector Contract
- PostgreSQL with `vector` extension enabled
- Column `embedding`: `Vector(384)`
- Cosine distance: `1 - (embedding <=> :job_vec)`

### Test Runner Commands
- Backend Integration: `uv run pytest tests/integration/`
- Contract Tests: `uv run pytest tests/contract/`
- Frontend Vitest: `pnpm run test` (in `web/`)
- Frontend Playwright: `pnpm exec playwright test` (in `web/`)
- Load Tests: `k6 run tests/load/k6_match_engine.js` (or via docker grafana/k6)

## Code Layout
- `.gemini/rules/testing-standards.md`
- `.gemini/rules/security-gates.md`
- `semgrep.yml`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `core/scoring/embeddings.py`
- `api/controllers/match.py`
- `api/controllers/marketplace.py`
- `migrations/versions/20260930_0001_initial_schema.py`
- `tests/integration/test_db_integration.py`
- `tests/contract/test_openapi.py`
- `web/package.json`
- `web/vitest.config.ts`
- `web/tests/components/Badge.test.tsx`
- `web/playwright.config.ts`
- `web/tests/e2e/marketplace.spec.ts`
- `tests/load/k6_match_engine.js`
