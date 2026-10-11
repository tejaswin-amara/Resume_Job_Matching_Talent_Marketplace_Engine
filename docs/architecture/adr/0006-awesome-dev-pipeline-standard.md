# 6. Awesome Dev Pipeline Standard Adoption

Date: 2026-10-11
Status: Accepted

## Context
As the Talent Marketplace Engine scales across algorithmic matching, semantic embeddings, real-time allocations, and multi-surface frontends, the system requires a unified, stack-aware engineering standard and operational defaults.

The codebase incorporates:
- A Python 3.12 backend (FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL with pgvector, OpenTelemetry).
- A TypeScript Next.js 14 frontend (React 18, Tailwind CSS, pnpm, Vitest, Playwright, React Bits animations).

To eliminate drift between CI gates, developer environments, and autonomous agent workflows, we adopt the **Awesome Dev Pipeline — Universal Engineering Standard & Agent Operating Defaults**.

## Decision
1. **Decision Hierarchy**: Adopt the 5-level precedence hierarchy (Rank 0: Safety/Legal, Rank 1: User instructions, Rank 2: Accepted ADRs, Rank 3: Existing conventions, Rank 4: Pipeline defaults).
2. **5-Phase Execution Protocol**: Enforce (1) Inspection & context, (2) Plan & validation strategy, (3) Incremental implementation, (4) Full quality gate, (5) Atomic Conventional Commits.
3. **Quality Gates per Stack**:
   - **Backend (Python)**: `uv run ruff check .` && `uv run ruff format --check .` && `uv run mypy --explicit-package-bases .` && `uv run python -m pytest tests/` && `gitleaks detect --redact --no-banner`.
   - **Frontend (TypeScript / Next.js)**: `pnpm run lint` && `pnpm run typecheck` && `pnpm test` && `pnpm exec playwright test` && `pnpm run build`.
   - **Motion-Heavy Frontend Profile**: Playwright tests must emulate both standard and `prefers-reduced-motion: reduce` configurations.
4. **Supply Chain & Security**:
   - All GitHub Actions must be pinned to full immutable commit SHAs with inline version comments.
   - Dependabot must maintain `github-actions`, `pip`, and `npm` ecosystems.
   - Workflows must run with explicit minimal permissions (`permissions: contents: read`).
   - Trivy actions must be pinned to specific SHA releases (addressing CVE-2026-33634) and paired with OSV-Scanner.
5. **Architectural Principles Preserved**:
   - FastAPI remains the authoritative API (`/api/v1/`). Next.js must not duplicate backend business logic.
   - Reference implementations remain forbidden as substitutes for testing production code paths.
   - No fake data in production endpoints; fail loudly on dependency failure.

## Consequences
- Mypy static analysis is strictly enforced in CI and local pre-commit hooks.
- Actions and container images are immutable and protected against supply chain injection.
- Consistent DX and reproducible testing across both local workstations and automated pipelines.
