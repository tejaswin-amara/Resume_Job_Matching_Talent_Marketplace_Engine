# Project: Awesome Dev Pipeline Audit Remediation (P0-P3)

## Architecture
The project remediates all P0-P3 issues across Security, Frontend Architecture, Core Algorithms, and CI/CD:
1. **Security & Reliability Tier (M1)**:
   - CORS in `api/app.py`: explicit origin whitelist (`settings.cors_origins`), eliminating wildcard credentials vulnerability.
   - Event loop resilience: wrapping CPU-intensive operations (resume parsing, neural embedding, skill extraction, graph matching) in `asyncio.to_thread`.
   - Health probes: `/health/ready` executes `await db.execute(text("SELECT 1"))` via AsyncSession, returning 503 on connection failure.
   - Database pooling: `create_async_engine` configured with `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`, `pool_recycle=3600`.
2. **Frontend Architecture Tier (M2)**:
   - React Bits exclusive UI: rip out all custom mock primitives in `web/src/components/ui/` (`badge.tsx`, `button.tsx`, `card.tsx`, `progress-bar.tsx`).
   - Implement React Bits components in `web/src/components/reactbits/` (`SpotlightCard`, `Squares`, `StarBorder`, `ShinyText`, `CountUp`, `AnimatedBadge`, `AnimatedProgress`).
   - Refactor Next.js pages (`page.tsx`, `candidates/page.tsx`, `recruiter/page.tsx`, `recruiter/allocate/page.tsx`) to consume React Bits exclusively.
   - Align Vitest tests (`Badge.test.tsx`) to React Bits primitives; keep Playwright E2E passing.
3. **Core Engine Algorithmic Tier (M3)**:
   - Dinic's Algorithm (`core/engine/flow/dinic.py`): verify and enforce `source == sink` returns `0.0` immediately.
   - Bitmask TSP (`core/engine/dp/bitmask_tsp.py`): verify tour reconstruction produces exactly $N+1$ nodes without duplicating start node.
   - Marketplace Network (`core/engine/flow/marketplace_network.py`): support `headcount` attribute and dictionary keys alongside `capacity` so multi-headcount job postings are respected.
   - Tree Reduction (`core/engine/randomised/parallel_primitives.py`): ensure identity element handling (`identity` parameter, neutral value for operator) does not violate mathematical invariants.
4. **CI/CD & DX Tier (M4)**:
   - Ruff linting: configure `exclude` in `pyproject.toml` for `scratch`, `.venv`, `.agents`, and ignore stylistic false-positives (`B008`, `E501`, `C901`, `PLR0913`); run `ruff check --fix` while strictly preserving zero-library imports in `core/engine/`.
   - GitHub Actions: pin `aquasecurity/trivy-action@0.28.0` in `.github/workflows/ci.yml`.
   - Docker: create `.dockerignore` ignoring `.git`, `.venv`, `node_modules`, `scratch`, `.agents`.
   - OpenTelemetry: configure basic OpenTelemetry Collector instrumentation (`api/telemetry/tracing.py`) and FastAPI instrumentation.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | CORS Whitelist | Replace wildcard origins with explicit origins in `api/app.py` | M1 | R1 |
| 2 | Async Thread Offloading | Wrap parsing, embedding, matching in `asyncio.to_thread` | M1 | R1 |
| 3 | Readiness Probe DB Ping | Execute `SELECT 1` in `/health/ready` probe | M1 | R1 |
| 4 | DB Connection Pooling | Configure `pool_pre_ping=True`, pool sizes in `db/session.py` | M1 | R1 |
| 5 | Remove Custom UI Primitives | Delete `web/src/components/ui/` mock shadcn primitives | M2 | R2 |
| 6 | React Bits Primitives | Create `web/src/components/reactbits/` component suite | M2 | R2 |
| 7 | Next.js Page Refactoring | Refactor Next.js pages to exclusively import React Bits | M2 | R2 |
| 8 | Frontend Test Alignment | Align `Badge.test.tsx` and Playwright tests to React Bits | M2 | R2 |
| 9 | Dinic source==sink Guard | Return 0.0 when source == sink in `dinic.py` | M3 | R3 |
| 10 | Bitmask TSP Tour Integrity | Enforce single visit per node and no extra start node | M3 | R3 |
| 11 | Marketplace Multi-Headcount | Respect `headcount` in `MarketplaceFlowNetwork` | M3 | R3 |
| 12 | Tree Reduction Identity | Monoid identity preservation in parallel reduction | M3 | R3 |
| 13 | Ruff Lint Cleanliness | Fix lint errors; zero ruff errors on `uv run ruff check .` | M4 | R4 |
| 14 | GitHub Actions Trivy Pin | Pin `aquasecurity/trivy-action@0.28.0` in `ci.yml` | M4 | R4 |
| 15 | .dockerignore Setup | Ignore `.git`, `.venv`, `node_modules`, `scratch` | M4 | R4 |
| 16 | Backend OpenTelemetry | Basic OTel collector instrumentation in `api/telemetry/` | M4 | R4 |
| 17 | Final Acceptance Gate | Full multi-tier test execution, reviews, challenge, audit | M5 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | R1 Security & Reliability | F1, F2, F3, F4 | none | DONE |
| 2 | R2 Frontend Architecture | F5, F6, F7, F8 | none | DONE |
| 3 | R3 Core Engine Defects | F9, F10, F11, F12 | none | DONE |
| 4 | R4 CI/CD & DX | F13, F14, F15, F16 | none | DONE |
| 5 | Acceptance Gate & Verification | F17 (2 Reviewers, 2 Challengers, Forensic Auditor) | M1, M2, M3, M4 | IN_PROGRESS |

## Interface Contracts
### Health Check
- `GET /health/ready`
- Returns: `200 {"status": "ready"}` if DB ping `SELECT 1` succeeds
- Returns: `503 {"status": "unhealthy", "detail": "Database unavailable"}` if DB ping fails

### Marketplace Flow Headcount
- `MarketplaceFlowNetwork.execute_allocation(candidates, jobs, capacities=None)`
- Job capacity resolves via `getattr(j, "headcount", getattr(j, "capacity", j.get("headcount", j.get("capacity", 1))))`

### React Bits Imports
- All UI components imported exclusively from `@/components/reactbits/*`
- No imports from `@/components/ui/*` or `shadcn`

## Code Layout
- `api/app.py`
- `api/config.py`
- `api/controllers/health.py`
- `api/controllers/resumes.py`
- `api/controllers/jobs.py`
- `api/controllers/match.py`
- `api/controllers/marketplace.py`
- `api/telemetry/tracing.py`
- `db/session.py`
- `core/engine/flow/dinic.py`
- `core/engine/dp/bitmask_tsp.py`
- `core/engine/flow/marketplace_network.py`
- `core/engine/randomised/parallel_primitives.py`
- `pyproject.toml`
- `.dockerignore`
- `.github/workflows/ci.yml`
- `web/src/components/reactbits/*`
- `web/src/app/*`
- `web/tests/components/Badge.test.tsx`
