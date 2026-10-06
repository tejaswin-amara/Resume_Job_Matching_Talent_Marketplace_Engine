# Progress Log - challenger_backend_reliability_1

- **Last visited**: 2026-10-06T04:15:30Z
- **Current status**: Testing complete. Writing handoff report and preparing orchestrator notification.

## Completed Verifications:
1. CORS Hardening: Verified that wildcard `*` with credentials is eliminated; disallowed origins receive no `Access-Control-Allow-Origin`; allowed origins receive credentials and origin headers.
2. Event Loop Non-blocking Behavior: Verified AST wrapping of `parser.parse`, `emb_service.encode`, `extractor.extract`, `matcher.match` in `asyncio.to_thread`. Empirically verified concurrent responsiveness (< 20ms probe latency) during real uploads and CPU offloads.
3. Database Readiness Probe: Verified `/health/ready` executes `SELECT 1` via `AsyncSession` and returns HTTP 503 upon operational failure, timeout, or unreachable database socket.
4. Lint Quality: Verified `uv run ruff check .` reports 0 errors across the codebase.
5. Docker Hygiene: Verified `.dockerignore` ignores `.git`, `.venv`, `node_modules`, `scratch`.
6. CI Security Action Pinning: Verified `aquasecurity/trivy-action@0.28.0` is pinned in `ci.yml`.
7. Empirical Defect Identification: Discovered and reproduced `fastapi.exceptions.ResponseValidationError: MissingGreenlet` on `POST /api/v1/jobs` and `GET /api/v1/jobs`. Also flagged `uv run ruff format --check .` failure on 6 files.
