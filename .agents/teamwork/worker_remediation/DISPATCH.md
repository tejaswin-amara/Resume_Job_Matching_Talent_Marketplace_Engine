## 2026-10-01T15:22:21Z

You are a Worker subagent (Remediation Specialist).
Your working directory is: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation
Your parent is: acfe1f8e-4ec5-49c0-b908-87c99fb5ba17

MANDATORY FIRST STEPS:
1. Append your dispatch message to .agents/teamwork/worker_remediation/DISPATCH.md with a UTC timestamp header.
2. Read the authoritative user request: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md (specifically ## 2026-09-30T15:18:26Z and Acceptance Criteria).
3. Read the Challenger reports with the specific defects to remediate:
   - c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_backend\handoff.md
   - c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_frontend_perf\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. An auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE FILE OWNERSHIP:
You EXCLUSIVELY own and may modify or create the following files:
- `api/controllers/match.py`
- `core/parsers/factory.py`
- `web/next.config.mjs` (create) and `web/next.config.ts` (delete)
- `api/controllers/marketplace.py`
- `semgrep.yml`
- `api/app.py`
- `tests/contract/test_openapi.py`

MISSION:
Execute the 6 targeted remediations to resolve all Challenger findings:

1. `api/controllers/match.py`:
   - Acceptance Criteria explicitly requires: `POST /api/v1/match/adhoc accepts raw resume text + job description, returns match result without persisting`.
   - Update `AdhocMatchRequest`:
     ```python
     class AdhocMatchRequest(BaseModel):
         resume_text: str
         job_description: str
         required_skills: list[str] = []
         min_experience: float = 0.0
         education_level: str | None = None
     ```
   - In `adhoc_match`: compute embeddings for `resume_text` and `job_description`, extract skills or use `required_skills`, run `HybridMatcher().match(...)`, and return the resulting `MatchResultResponse` transiently WITHOUT persisting to the database (no `db.add`, no `db.commit`).
2. `core/parsers/factory.py`:
   - In `ParserFactory.from_content_type`: guard against `content_type is None` or invalid types. If `content_type is None`, fall back to `TextParser` or raise `ValueError`.
3. `web/next.config.mjs`:
   - Create `web/next.config.mjs`:
     ```javascript
     /** @type {import('next').NextConfig} */
     const nextConfig = {
       reactStrictMode: true,
     };
     export default nextConfig;
     ```
   - Remove `web/next.config.ts` so Next.js 14 recognizes `next.config.mjs` cleanly.
   - Run `pnpm exec playwright test --list` in `web/` to confirm clean configuration.
4. `api/controllers/marketplace.py`:
   - Harden `RecruiterMatchRequest`:
     `candidate_limit: int = Field(default=10, ge=1, le=100)`
     Deduplicate `required_skills`: `deduped_skills = list(dict.fromkeys(req.required_skills))`
5. `semgrep.yml`:
   - Fix `missing-request-timeout` pattern so metavariables are well-formed.
   - Run Python YAML validation on `semgrep.yml`.
6. `api/app.py`:
   - Harden `CORSMiddleware`: set `allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]` with `allow_credentials=True` so wildcard credentials violation is resolved.
7. Verification:
   - Run `uv run pytest tests/contract/test_openapi.py -v`
   - In `web/`: run `pnpm run test`
   - In `web/`: run `pnpm exec playwright test --list`
   - Run `k6 run tests/load/k6_match_engine.js` (or via C:\Program Files\k6\k6.exe)
   - Run `uv run ruff check api/ core/ tests/`
   - Document all execution commands and outputs in your report.
8. Write your completion report to:
   `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation\handoff.md`
9. Notify parent via send_message when complete.
