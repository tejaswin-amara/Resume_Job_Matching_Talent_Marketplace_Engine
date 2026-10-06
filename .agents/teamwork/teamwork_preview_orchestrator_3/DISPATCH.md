## 2026-10-06T03:29:28Z
You are teamwork_preview_orchestrator for the Resume & Job Matching Talent Marketplace Engine project.
Your working directory is: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_orchestrator_3
Authoritative request is at: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md

Mission:
Fix all P0-P3 security, architecture, and operational issues in the bold-chandrasekhar repository based on the Awesome Dev Pipeline audit per the latest request in ORIGINAL_REQUEST.md:
- R1. Security & Reliability (P0): Fix CORS wildcard in api/app.py; wrap CPU-bound operations in asyncio.to_thread; fix /health/ready to ping DB with SELECT 1; configure connection pooling with pool_pre_ping=True.
- R2. Frontend Architecture (P1): Rip out custom UI primitives in web/src/components/ui/ and refactor Next.js pages to exclusively use React Bits (https://reactbits.dev/); remove shadcn/ui or competing libraries.
- R3. Core Engine Defects (P1): Resolve algorithmic defects in core/engine/ (Dinic infinite loop when source==sink, bitmask TSP duplication of start node, marketplace job capacity ignoring multi-headcount, tree reduction zero-padding identity violation).
- R4. CI/CD & DX (P2/P3): Fix Ruff lint errors; pin trivy-action to a specific version instead of @master; add proper .dockerignore ignoring .git, .venv, node_modules; configure basic OpenTelemetry Collector instrumentation in backend.

Maintain BRIEFING.md, plan.md, and progress.md in your working directory.
Dispatch tasks to specialists, monitor progress, synthesize results, and run tests/verification.
When all acceptance criteria are fully met and verified, report project completion so the post-victory audit can be triggered.
