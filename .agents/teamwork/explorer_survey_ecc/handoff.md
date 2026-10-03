# Handoff Report: Requirement R1 (ECC Rules Integration Survey)

**Agent**: explorer_survey_ecc  
**Working Directory**: `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\explorer_survey_ecc`  
**Mission**: Investigate `scratch/ecc-repo` to extract testing-specific skills and security validation rules and formulate concrete content recommendations for `.gemini/rules/testing-standards.md` and `.gemini/rules/security-gates.md`.

---

## 1. Observation

A comprehensive inspection of the `scratch/ecc-repo` repository was conducted across its rules, skills, documentation, and agent specifications. The following concrete files and rules were examined:

### A. Testing Rules and Skills in `scratch/ecc-repo`

1. **`scratch/ecc-repo/rules/common/testing.md` (Lines 1–58)**:
   - Coverage: Minimum test coverage standard is **80%**.
   - Test Types: Mandates three primary tiers: **Unit Tests** (functions, utilities, components), **Integration Tests** (API endpoints, database operations), and **E2E Tests** (critical user flows).
   - TDD Methodology: Red-Green-Refactor cycle:
     1. Write test first (RED)
     2. Run test - it should FAIL
     3. Write minimal implementation (GREEN)
     4. Run test - it should PASS
     5. Refactor (IMPROVE)
     6. Verify coverage (80%+)
   - Test Structure: Mandates Arrange-Act-Assert (AAA) pattern.
   - Test Naming: Descriptive behavior-driven naming (e.g. `test_returns_empty_when_no_match`).

2. **`scratch/ecc-repo/rules/python/testing.md` (Lines 1–39)**:
   - Framework: Standardizes on `pytest` and `pytest-cov`:
     ```bash
     pytest --cov=src --cov-report=term-missing
     ```
   - Categorization: Mandates `@pytest.mark.unit` and `@pytest.mark.integration`.
   - References `skills/python-testing` for detailed fixture and mock patterns.

3. **`scratch/ecc-repo/rules/python/fastapi.md` (Lines 1–59)**:
   - Architecture & DI: Mandates thin routers, `Depends()` for database sessions and auth, and clearing `app.dependency_overrides` after tests.
   - Async Rules: Endpoints performing I/O must be `async def` and use async database/HTTP clients without blocking sync calls.
   - Schema & Security: Mandates response models on endpoints, strict field constraints, separate schemas for request/update/response, and forbids leaking password hashes, internal tokens, or secrets.

4. **`scratch/ecc-repo/rules/react/testing.md` (Lines 1–150)**:
   - Runner: Prefers **Vitest** for modern Vite/Next.js stacks ("faster than Jest, native ESM").
   - Principle: "Test what the user sees and does, not implementation details."
   - Query Priority: Accessible queries first (`getByRole`, `getByLabelText`, `getByPlaceholderText`, `getByText`), falling back to `getByTestId` only when necessary.
   - User Events: Mandates `userEvent` over synthetic `fireEvent`.
   - Async Assertions: Mandates `findBy*` or `waitFor()` instead of arbitrary delays.
   - Browser Testing: Directs real-browser end-to-end testing to Playwright.

5. **`scratch/ecc-repo/skills/python-testing/SKILL.md` (Lines 1–818)**:
   - Fixture architecture: Modular fixture scoping (`function`, `module`, `session`), setup/teardown with `yield`, and `tests/conftest.py` shared fixtures.
   - Parametrization: `@pytest.mark.parametrize` with explicit `ids` for edge cases (zero division, empty arrays, null values, unicode).
   - Async testing: `pytest-asyncio` with `async def test_*` and async client fixtures.
   - Mocking standards: Mock external APIs and avoid mocking internal implementation details.

6. **`scratch/ecc-repo/skills/contract-first/SKILL.md` (Lines 1–288)**:
   - Canonical boundary artifact: OpenAPI 3.1 schema.
   - Machine-checkable contract verification between provider (FastAPI) and consumer (Next.js).
   - Verifies provider responses against the schema to eliminate field drift, schema mismatches, and undocumented error codes.

7. **`scratch/ecc-repo/skills/e2e-testing/SKILL.md` (Lines 1–328)**:
   - Framework: Playwright (`@playwright/test`).
   - Pattern: Page Object Model (POM) for maintainable selectors and user flows.
   - Flakiness prevention: Auto-wait locators (`locator.click()`), waiting on network responses (`waitForResponse`), never using arbitrary timeouts (`waitForTimeout`).
   - Artifacts: Automatic capture of screenshots, videos, and trace files on failure.

8. **`scratch/ecc-repo/skills/benchmark/SKILL.md` (Lines 1–96)**:
   - Mode 2 (API Performance): Hit endpoints under load (e.g. 10+ concurrent requests), measure latency percentiles (**p50, p95, p99**), track response sizes and error rates, compare against SLA targets.
   - Baseline regression tracking: PR-level performance checks against git-tracked metrics.

---

### B. Security Gates and Validation Rules in `scratch/ecc-repo`

1. **`scratch/ecc-repo/rules/common/security.md` (Lines 1–30)**:
   - Mandatory Pre-Commit Security Checks:
     - No hardcoded secrets (API keys, passwords, tokens)
     - All user inputs validated
     - SQL injection prevention (parameterized queries)
     - XSS prevention (sanitized HTML)
     - CSRF protection enabled
     - Authentication/authorization verified
     - Rate limiting on all endpoints
     - Error messages don't leak sensitive data
   - Protocol: If a critical security issue is found, STOP immediately, fix before continuing, rotate exposed secrets.

2. **`scratch/ecc-repo/rules/python/security.md` (Lines 1–31)**:
   - Secret Management: Environment variables (`os.environ["..."]`) with startup checks that fail fast if missing.
   - Static analysis: Running security linters like `bandit -r src/`.

3. **`scratch/ecc-repo/skills/security-review/SKILL.md` (Lines 1–512)**:
   - Comprehensive vulnerability taxonomy across 10 domains:
     - 1. Secrets Management: Zero hardcoded secrets, `.env*` in `.gitignore`, startup validation.
     - 2. Input Validation: Schema enforcement, file upload type/size/extension whitelisting.
     - 3. SQL Injection: Parameterized queries, ORM safety.
     - 4. Authentication/Authorization: Secure cookie attributes (`HttpOnly; Secure; SameSite=Strict`), role-based checks.
     - 5. XSS Prevention: Sanitizing user HTML (DOMPurify), CSP headers.
     - 6. CSRF: Tokens for mutating requests, SameSite cookies.
     - 7. Rate Limiting: Endpoint rate limiting and stricter limits on expensive operations.
     - 8. Sensitive Data Exposure: Masking PII/credentials in logs, generic client error messages.
     - 9. Dependency Security: `npm audit`, lockfile enforcement.

4. **`scratch/ecc-repo/skills/security-bounty-hunter/SKILL.md` (Lines 1–101)**:
   - Automated SAST triage loop:
     ```bash
     semgrep --config=auto --severity=ERROR --severity=WARNING --json
     ```
   - In-scope pattern checklist: SSRF (CWE-918), Auth bypass (CWE-287), Deserialization/RCE (CWE-502), SQL injection (CWE-89), Command injection (CWE-78), Path traversal (CWE-22), XSS (CWE-79).

5. **`scratch/ecc-repo/skills/django-verification/SKILL.md` (Lines 120–144, 438–453)**:
   - Phased Security Scan commands:
     - Secret scanning: `gitleaks detect --source . --verbose`
     - Python SAST: `bandit -r . -f json -o bandit-report.json`
     - Dependency audit: `pip-audit` and `safety check`
     - CI integration workflow with PostgreSQL services, lint, security scans, and test execution.

6. **`scratch/ecc-repo/the-security-guide.md` (Lines 1–464)** & **`skills/gateguard/SKILL.md`**:
   - Least Agency doctrine: Restrict tool permissions, enforce isolated environments (containers/devcontainers).
   - Sanitization of untrusted text: Quarantining incoming resumes/job descriptions/PDFs/untrusted inputs before NLP/embedding ingestion to neutralize indirect prompt injection and hidden payloads.
   - Deterministic delivery gates: Machine-verifiable checks (linter, test suite, secret scans) must pass before declaring delivery complete.

---

## 2. Logic Chain

1. **Alignment with Authoritative Requirements (ORIGINAL_REQUEST.md & R1–R5)**:
   - Requirement R1 explicitly specifies: *"Extract testing-specific skills and security validation rules from the `affaan-m/ECC` repository (already cloned to `scratch/ecc-repo`) and configure them locally within the project (e.g. `.gemini/rules/testing-standards.md`, `.gemini/rules/security-gates.md`) to empower autonomous testing and security scans."*
   - Requirements R2–R5 detail the exact verification layers:
     - R2: PostgreSQL testcontainers integration testing + Schemathesis OpenAPI contract testing.
     - R3: Next.js Vitest component tests + Playwright E2E tests.
     - R4: k6 concurrency load testing on `/api/v1/marketplace/match` measuring p95 latency.
     - R5: Semgrep custom rules (`semgrep.yml`), Gitleaks secret scanning, Trivy container/dependency scanning, CI workflow integration aligned with Ponytail minimalism.

2. **Synthesis of ECC Rules into `.gemini/rules/testing-standards.md`**:
   - From `rules/common/testing.md` and `skills/python-testing`, we extract the universal 80% coverage mandate, TDD workflow (RED-GREEN-REFACTOR), and AAA pattern.
   - From `rules/python/testing.md` and `skills/python-testing`, we extract pytest test structure, markers (`unit`, `integration`, `contract`), and testcontainers database testing standards.
   - From `skills/contract-first`, we extract OpenAPI contract verification and Schemathesis fuzzing rules.
   - From `rules/react/testing.md` and `skills/e2e-testing`, we extract Next.js Vitest component testing guidelines (accessible queries, userEvent) and Playwright E2E standards (Page Object Model, network idle synchronization, artifact capture).
   - From `skills/benchmark`, we extract the k6 load testing specification, defining p95 latency targets (<200ms) and concurrency benchmarks.

3. **Synthesis of ECC Rules into `.gemini/rules/security-gates.md`**:
   - From `rules/common/security.md` and `skills/security-review`, we extract the 4-gate verification model: Secret Scanning, SAST, Dependency Scanning, and Runtime Application Hardening.
   - From `skills/django-verification` and `the-security-guide.md`, we extract exact tool configurations: `gitleaks detect` for secrets, `semgrep` + `bandit` for SAST, and `trivy fs .` + `pip-audit` for dependencies.
   - From `rules/python/fastapi.md` and `the-security-guide.md`, we extract FastAPI-specific hardening: Pydantic response filtering (never leaking tokens/hashes), CORS lockdown, input sanitization against prompt injection in resume PDFs/DOCX, and generic error handlers.
   - From `skills/delivery-gate`, we extract deterministic CI blocking gates: zero tolerance for CRITICAL/HIGH vulnerabilities or secret leaks.

4. **Integration with Antigravity Project Architecture**:
   - The project has a zero-library algorithmic core in `core/engine/`, a FastAPI layer in `api/`, and a Next.js frontend in `web/`.
   - The testing standards and security gates must directly reflect these boundaries, enforcing strict separation of concerns, test isolation, and automated CI gating.

---

## 3. Caveats

1. **Read-Only Explorer Scope**: This investigation did not generate or edit project code or rules files outside `.agents/teamwork/explorer_survey_ecc/`. Implementation of `.gemini/rules/testing-standards.md` and `.gemini/rules/security-gates.md` must be completed by the implementation agent.
2. **Local Tooling Availability**: Some CLI tools (e.g. `gitleaks`, `trivy`, `k6`) may need to be invoked via Docker, npx, or CI actions if not globally installed on the local developer environment. The rules provide both local and CI invocation paths.
3. **Vitest / Playwright in `web/`**: The frontend directory `web/` currently uses Next.js with `pnpm`; package additions (`vitest`, `@testing-library/react`, `@playwright/test`) must be installed in `web/` during R3.

---

## 4. Conclusion & Recommended Content

### A. Recommended Content for `.gemini/rules/testing-standards.md`

The recommended content to place into `.gemini/rules/testing-standards.md` is structured into five operational sections:

```markdown
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
  - 95th percentile latency (p95) < 200ms under 20 concurrent VUs.
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
```

---

### B. Recommended Content for `.gemini/rules/security-gates.md`

The recommended content to place into `.gemini/rules/security-gates.md` is structured into five operational sections:

```markdown
---
description: Mandatory security gates, vulnerability mitigation policies, and CI supply chain checks (Secret scanning, SAST, Dependency scanning).
globs: ["**/*"]
---

# Security Gates & Vulnerability Mitigation Policy

Derived from ECC security patterns and agentic security standards for the Talent Marketplace Engine.

## 1. Core Security Doctrine

- **Least Agency & Defense in Depth**: Minimize attack surface across API boundaries, background tasks, and agent execution.
- **Fail Closed**: Incomplete or failing security checks unconditionally block CI pipelines and production releases.
- **No Trust for External Input**: Resumes (PDF, DOCX, text) and job postings are treated as untrusted data payloads; strict quarantine and sanitization are applied before NLP parsing and vector embedding generation to prevent prompt injection and deserialization attacks.

## 2. Four Mandatory Security Gates

### Gate 1: Secret Scanning (`gitleaks`)
- **Standard**: Zero hardcoded secrets, private keys, API tokens, database credentials, or environment files in the Git tree.
- **Enforcement**:
  - Run `gitleaks detect --source . --verbose` locally and in CI.
  - Keep `.env`, `.env.local`, and sensitive configuration in `.gitignore`.
  - Validate all required environment variables at application startup, failing fast with informative messages if missing.

### Gate 2: Static Application Security Testing / SAST (`semgrep` + `bandit`)
- **Standard**: Block OWASP Top 10 vulnerabilities, specifically:
  - SQL Injection (CWE-89): Enforce SQLAlchemy ORM / parameterized queries; forbid raw string interpolation.
  - Command Injection (CWE-78): Forbid unsanitized shell invocations (`os.system`, `subprocess.Popen(..., shell=True)`).
  - Path Traversal (CWE-22): Validate all resume file uploads; enforce safe basename generation and extension whitelisting (`.pdf`, `.docx`, `.txt`).
  - SSRF (CWE-918): External public-apis enrichment calls must validate target hosts against an allowlist and enforce 3-5s timeouts.
- **Enforcement**:
  - Run `semgrep --config semgrep.yml --error` to evaluate custom and standard security rules.
  - Run `bandit -r api/ core/ db/ -ll` for Python AST static analysis.

### Gate 3: Dependency & Supply Chain Scanning (`trivy` + `pip-audit`)
- **Standard**: Zero critical or high known CVEs in application dependencies, container images, or lockfiles.
- **Enforcement**:
  - Backend: `pip-audit` or `trivy fs . --severity HIGH,CRITICAL` scanning `uv.lock`.
  - Frontend: `pnpm audit --audit-level=high` scanning `web/pnpm-lock.yaml`.
  - Always commit lockfiles to maintain deterministic, reproducible builds.

### Gate 4: API & Web Application Hardening
- **FastAPI Endpoint Security**:
  - Response models: Strictly define Pydantic response models; never expose password hashes, internal tokens, or database internals.
  - CORS configuration: Explicitly configure allowed origins (`allow_origins`); forbid wildcard `*` when credentials are permitted.
  - Rate limiting: Apply rate limiting on resume upload, job creation, and heavy matching computation endpoints.
  - Error handling: Never return raw stack traces or internal exception details to API clients. Return structured Problem Details (RFC 7807).

## 3. CI/CD Pipeline Enforcement (`.github/workflows/ci.yml`)

The CI workflow must execute the following sequential stages:
1. **Lint & Format**: Ruff check/format (Python), Biome check (TypeScript).
2. **Security Gates**:
   - `gitleaks detect` (Secret scanning)
   - `semgrep ci` (Static analysis with `semgrep.yml`)
   - `trivy fs --severity HIGH,CRITICAL .` (Vulnerability scanning)
3. **Backend Test Suite**:
   - Algorithmic unit tests (`uv run pytest tests/unit/`)
   - Testcontainers DB integration tests (`uv run pytest tests/integration/`)
   - Contract tests (`uv run pytest tests/contract/`)
4. **Frontend Test Suite**:
   - Vitest component tests (`pnpm run test`)
   - Playwright E2E tests (`pnpm exec playwright test`)
5. **Docker Build Verification**: Docker build of backend and frontend containers.

## 4. Pre-Flight Security Checklist

Before merging PRs or tagging releases:
- [ ] `gitleaks detect` reports 0 secrets found.
- [ ] `semgrep` reports 0 ERRORs.
- [ ] `pip-audit` / `trivy` reports 0 HIGH/CRITICAL vulnerabilities.
- [ ] No unparameterized SQL queries in codebase.
- [ ] Resume upload file extension and MIME type validation active.
- [ ] All API responses use validated Pydantic schemas.
- [ ] Health check endpoints (`/health/live`, `/health/ready`) return 200 without exposing telemetry secrets.
```

---

## 5. Verification Method

To verify these survey findings and ensure the proposed rules can be independently reviewed:

1. **Inspect ECC Source Files**:
   - `scratch/ecc-repo/rules/common/testing.md`
   - `scratch/ecc-repo/rules/common/security.md`
   - `scratch/ecc-repo/rules/python/testing.md`
   - `scratch/ecc-repo/rules/python/fastapi.md`
   - `scratch/ecc-repo/rules/react/testing.md`
   - `scratch/ecc-repo/skills/python-testing/SKILL.md`
   - `scratch/ecc-repo/skills/contract-first/SKILL.md`
   - `scratch/ecc-repo/skills/e2e-testing/SKILL.md`
   - `scratch/ecc-repo/skills/benchmark/SKILL.md`
   - `scratch/ecc-repo/skills/security-review/SKILL.md`
   - `scratch/ecc-repo/skills/django-verification/SKILL.md`
   - `scratch/ecc-repo/skills/security-bounty-hunter/SKILL.md`
   - `scratch/ecc-repo/the-security-guide.md`

2. **Downstream Implementation Check**:
   - When the builder agent implements Requirement R1, verify that `.gemini/rules/testing-standards.md` and `.gemini/rules/security-gates.md` are created with the exact structure outlined above.
   - Verify that the rules empower requirements R2 (Testcontainers & Schemathesis), R3 (Vitest & Playwright), R4 (k6), and R5 (Gitleaks, Semgrep, Trivy).
