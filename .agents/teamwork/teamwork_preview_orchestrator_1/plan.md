# Project Master Plan

## Objective
Build a production-grade Resume & Job Matching Talent Marketplace Engine according to ORIGINAL_REQUEST.md.

## Execution Pattern: Project Pattern (Dual Track)
1. **Survey (Phase 0)**:
   - Spawn 3 parallel survey explorers / spec miners to thoroughly analyze requirements, tech stack (FastAPI, pgvector, Next.js, sentence-transformers, Alembic, Docker, Biome, Ruff), dependencies, APIs, and edge cases.
   - Aggregate findings and synthesize into `PROJECT.md` at project root with Feature Inventory, Milestones, Architecture, Code Layout, and Interface Contracts.

2. **Dual Track Dispatch (Phase 1)**:
   - **Track 1: E2E Testing Track**:
     - Spawn test writer / E2E specialist to design opaque-box test runner and test cases for Tiers 1-4 (>=11*N + max(5, N/2) test cases).
     - Produce `TEST_INFRA.md` and publish `TEST_READY.md`.
   - **Track 2: Implementation Track**:
     - Milestone 1: Backend Data Layer & Database (PostgreSQL + pgvector, SQLAlchemy models, Alembic migrations, database connection pooling, seed script with >=10 jobs and >=15 candidates).
     - Milestone 2: ML/NLP Matching Engine & Parser (Sentence-transformers embeddings, hybrid scoring math 40/35/15/10, ATS explainability breakdown, edge cases handling, resume entity extraction for PDF/DOCX/text).
     - Milestone 3: Backend REST API & Services (FastAPI routes: /api/v1/resumes/upload, /api/v1/jobs CRUD, /api/v1/jobs/{id}/matches, /api/v1/match/adhoc, /health/live, /health/ready, RFC7807 error responses, CORS, middleware).
     - Milestone 4: Frontend Web Application (Next.js 14/15 App Router, TypeScript, Tailwind CSS, dark-mode-first, Candidate portal with drag-and-drop resume upload & diagnostic feedback, Recruiter portal with job postings & ranked leaderboard & skill gap visualization).
     - Milestone 5: Infrastructure & DevOps (Docker Compose with healthchecks, GitHub Actions CI workflow, Ruff and Biome configurations, README with architecture diagrams and quickstart, .env.example, .gitignore).

3. **Verification & Hardening (Phases 2-5)**:
   - Run full E2E test suite (100% pass on Tiers 1-4).
   - Adversarial coverage hardening (Tier 5): Challenger loop on edge cases, zero-division, boundary scores.
   - Forensic integrity audit (clean check, zero tolerance for hardcoded values).

4. **Completion & Final Report**:
   - Synthesize all artifacts, verify passing test logs and clean audit, and report to Sentinel.
