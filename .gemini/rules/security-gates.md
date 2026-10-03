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
