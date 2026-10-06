# Dispatch: Challenger 2 (Backend Reliability & Security Stress Verification)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_backend_reliability_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Worker Handoff Report
- Worker 1 (M1 & M4): `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m1_m4_1\handoff.md`

## Challenge Scope & Instructions
Adversarially challenge backend security and reliability fixes:
1. **CORS Hardening**:
   - Verify that `allow_origins=["*"]` with `allow_credentials=True` is gone.
   - Test that requests with disallowed origins are rejected or do not receive `Access-Control-Allow-Origin: *` with credentials.
2. **Event Loop Non-blocking Behavior**:
   - Verify that heavy CPU routes (`/api/v1/resumes/upload`, `/api/v1/jobs`, `/api/v1/match/adhoc`) wrap CPU tasks in `asyncio.to_thread`.
   - Test concurrent calls to ensure that the event loop does not freeze and lightweight I/O routes (like `/health/live`) remain responsive during CPU tasks.
3. **Readiness Probe**:
   - Verify that `/health/ready` executes `SELECT 1` via `AsyncSession`.
   - Test failure scenario: when DB connection fails or is simulated down, `/health/ready` returns HTTP 503 instead of 200.
4. **CI/CD & Lint Quality**:
   - Run `uv run ruff check .` and verify 0 errors across the codebase.
   - Verify `.dockerignore` ignores `.git`, `.venv`, `node_modules`, `scratch`.
   - Verify `ci.yml` pins `aquasecurity/trivy-action@0.28.0`.

Deliver your verdict (`APPROVE` or `REQUEST_CHANGES`) with empirical test data in `handoff.md`.

## 2026-10-06T04:06:03Z
You are a Challenger subagent for the Resume & Job Matching Talent Marketplace Engine project.
Your identity: challenger_backend_reliability_1
Your working directory: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_backend_reliability_1

MANDATORY FIRST STEP: Read the authoritative user request at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md
Also read your assignment at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_backend_reliability_1\DISPATCH.md
And the worker handoff at:
- `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m1_m4_1\handoff.md`

Adversarially challenge backend security, reliability, and CI:
- Verify CORS wildcard rejection.
- Verify CPU routes use `asyncio.to_thread` and do not block the event loop under concurrent load.
- Verify `/health/ready` executes `SELECT 1` DB ping and returns 503 on database failure.
- Verify `uv run ruff check .` reports 0 errors.
- Verify `.dockerignore` ignores `.git`, `.venv`, `node_modules`, `scratch`.
- Verify `.github/workflows/ci.yml` pins `aquasecurity/trivy-action@0.28.0`.
Write your findings and verdict (APPROVE or REQUEST_CHANGES) to:
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_backend_reliability_1\handoff.md`
and notify me via send_message when complete.
