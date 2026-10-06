# Dispatch: Worker M1 & M4 (Backend Security, Reliability, CI/CD, OpenTelemetry)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m1_m4_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Explorer Investigation Report
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r1_r4_1\handoff.md`

## Scope & File Ownership
You exclusively own and modify:
- `api/app.py`
- `api/config.py`
- `api/controllers/health.py`
- `api/controllers/resumes.py`
- `api/controllers/jobs.py`
- `api/controllers/match.py`
- `db/session.py`
- `api/telemetry/` (new files, e.g. `api/telemetry/tracing.py`)
- `pyproject.toml`
- `.dockerignore` (new file)
- `.github/workflows/ci.yml`

## Objectives
1. **CORS Fix (`api/app.py`)**:
   - In `api/config.py`, add `cors_origins: list[str] = ["http://localhost:3000"]` (or comma-separated env parsing).
   - In `api/app.py`, update `CORSMiddleware`:
     `allow_origins=settings.cors_origins` (or `["http://localhost:3000"]`), `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
     Ensure `allow_origins=["*"]` with `allow_credentials=True` is completely gone.
2. **`asyncio.to_thread` Wrapping**:
   - `api/controllers/resumes.py`: wrap `parser.parse(content)`, `emb_service.encode(text)`, `extractor.extract(text)` in `await asyncio.to_thread(...)`. In `parse_text`, also wrap `extractor.extract(text)`.
   - `api/controllers/jobs.py`: wrap `emb_service.encode(text)` in `await asyncio.to_thread(...)`.
   - `api/controllers/match.py`: wrap `matcher.match(...)` in `await asyncio.to_thread(...)`.
3. **Readiness Probe (`api/controllers/health.py`)**:
   - In `api/controllers/health.py`, update `/ready` endpoint to accept `db: AsyncSession = Depends(get_db_session)`.
   - Execute `await db.execute(text("SELECT 1"))`. Return `{"status": "ready"}` on success.
   - On exception / database error, raise `HTTPException(status_code=503, detail="Database unavailable")`.
4. **Database Connection Pooling (`db/session.py`)**:
   - In `db/session.py`, update `create_async_engine`:
     Add `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`, `pool_recycle=3600`, `pool_timeout=30.0`.
5. **OpenTelemetry Instrumentation**:
   - Create `api/telemetry/tracing.py` configuring basic OpenTelemetry Collector tracing (with fallback if OTLP collector is not reachable or packages not installed, or using standard `opentelemetry` tracer provider). Wire tracing setup into `api/app.py`.
6. **Pin Trivy Action (`.github/workflows/ci.yml`)**:
   - In `.github/workflows/ci.yml`, change `aquasecurity/trivy-action@master` to `aquasecurity/trivy-action@0.28.0`.
7. **Create `.dockerignore`**:
   - Create `.dockerignore` in root with `.git`, `.venv`, `node_modules`, `scratch`, `.agents`, `__pycache__`, `*.pyc`, `.pytest_cache`, `.coverage`, `dist`, `build`.
8. **Ruff Linting**:
   - In `pyproject.toml`, add `exclude = ["scratch", "web", ".venv", ".agents"]`.
   - Adjust `[tool.ruff.lint]` ignore list to ignore `["B008", "E501", "C901", "PLR0913", "PLR2004", "PLR0912"]` and add per-file ignores as needed so legitimate algorithmic and FastAPI dependency injection code passes cleanly.
   - Run `uv run ruff check .` and fix all remaining lint errors until it exits with code 0.
   - IMPORTANT: DO NOT add `from collections.abc import ...` into `core/engine/`!

## Verification Required
- Run `uv run ruff check .` and verify 0 errors.
- Run `uv run pytest tests/unit/` and verify all tests pass.
- Run `uv run pytest tests/contract/` and verify passing.
- Output full results in `handoff.md`.


## 2026-10-06T03:43:44Z
You are a Worker subagent for the Resume & Job Matching Talent Marketplace Engine project.
Your identity: worker_remediation_m1_m4_1
Your working directory: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m1_m4_1

MANDATORY FIRST STEP: Read the authoritative user request at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md
Also read the investigation report at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r1_r4_1\handoff.md
And your detailed task instructions at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m1_m4_1\DISPATCH.md

Scope & File Ownership:
You exclusively own and modify:
- `api/app.py`
- `api/config.py`
- `api/controllers/health.py`
- `api/controllers/resumes.py`
- `api/controllers/jobs.py`
- `api/controllers/match.py`
- `db/session.py`
- `api/telemetry/`
- `pyproject.toml`
- `.dockerignore`
- `.github/workflows/ci.yml`

Implement all requirements for M1 (Security & Reliability: CORS wildcard fix, asyncio.to_thread wrapping on CPU routes, /health/ready DB ping with SELECT 1, pool_pre_ping=True and connection pooling in db/session.py) and M4 (CI/CD & DX: ruff configuration and zero errors on `uv run ruff check .`, pin trivy-action to 0.28.0 in ci.yml, create .dockerignore, basic OpenTelemetry instrumentation in api/telemetry/).
