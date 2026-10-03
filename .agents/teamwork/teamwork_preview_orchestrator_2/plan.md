# Execution Plan: Awesome Dev Pipeline Verification Matrix & Security Gates

## Goal
Implement and verify all 5 requirements (R1 - R5) and satisfy all 6 acceptance criteria for the Resume_Job_Matching_Talent_Marketplace_Engine.

## Phases
1. **Phase 0: Survey & Inventory**
   - Explorer 1: Survey `scratch/ecc-repo`, testing skills, security validation rules, rule extraction targets (`.gemini/rules/testing-standards.md`, `.gemini/rules/security-gates.md`).
   - Explorer 2: Survey backend setup (`pyproject.toml`, existing DB models, migrations, FastAPI app, routes, existing tests). Determine testcontainers, schemathesis, httpx setup.
   - Explorer 3: Survey frontend (`web/`, `package.json`, Next.js app, Vitest/Playwright readiness), load testing (`tests/load/k6_match_engine.js`), and CI/security (`.github/workflows/ci.yml`, `semgrep.yml`).

2. **Phase 1: M1 - ECC Rules Integration (R1)**
   - Extract testing-specific skills and security validation rules from `scratch/ecc-repo`.
   - Configure local rules at `.gemini/rules/testing-standards.md` and `.gemini/rules/security-gates.md`.

3. **Phase 2: M2 - Backend Verification Matrix (R2)**
   - Update `pyproject.toml` with `testcontainers`, `schemathesis`, `locust`, `httpx` in dev dependencies.
   - Implement `tests/integration/test_db_integration.py` (testcontainers PostgreSQL with pgvector, Alembic migrations, hybrid scoring verification).
   - Implement `tests/contract/test_openapi.py` (schemathesis fuzzing / contract check on FastAPI OpenAPI schema).
   - Run verification via worker.

4. **Phase 3: M3 - Frontend Verification Matrix (R3)**
   - Configure `web/vitest.config.ts` and component test in `web/tests/components/`.
   - Configure `web/playwright.config.ts` and E2E test in `web/tests/e2e/marketplace.spec.ts`.
   - Run Vitest and Playwright checks.

5. **Phase 4: M4 - Performance & Load Testing (R4)**
   - Implement `tests/load/k6_match_engine.js` simulating concurrent recruiters against `/api/v1/marketplace/match`.
   - Run k6 test and verify HTTP 200 checks pass.

6. **Phase 5: M5 - Security & Supply Chain Gates (R5)**
   - Implement `semgrep.yml` with project-specific rules.
   - Update `.github/workflows/ci.yml` with gitleaks, semgrep, trivy steps.

7. **Phase 6: Final Verification & Acceptance Gate**
   - Reviewer, Challenger, and Auditor validation across all acceptance criteria.
   - Compile final verification report.
