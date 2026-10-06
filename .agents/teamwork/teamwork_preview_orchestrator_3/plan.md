# Plan: Awesome Dev Pipeline Audit Remediation (P0-P3)

## Objective
Remediate all issues identified in the audit per ORIGINAL_REQUEST.md (2026-10-06T03:27:21Z):
- R1: Security & Reliability (P0) — CORS, asyncio.to_thread, DB ping, pool_pre_ping
- R2: Frontend Architecture (P1) — React Bits exclusive UI, eliminate custom ui / shadcn
- R3: Core Engine Defects (P1) — Dinic loop, TSP tour duplication, job capacity multi-headcount, tree reduction identity
- R4: CI/CD & DX (P2/P3) — Ruff lint clean, trivy-action pinned, .dockerignore, OpenTelemetry backend instrumentation

## Phases

### Phase 0: Survey & Investigation
- Dispatch 3 Explorers in parallel:
  - Explorer 1: R1 & R4 (Backend API security, reliability, pooling, OpenTelemetry, CI/CD, lint, dockerignore)
  - Explorer 2: R2 (Frontend architecture, web/src/components/ui/, React Bits requirements)
  - Explorer 3: R3 (Core Engine algorithmic defects in flow, dp, marketplace, randomized tree reduction)
- Aggregate findings into `PROJECT.md` (Feature Inventory, Milestones, Contracts).

### Phase 1: Remediation Execution (Workers)
- Worker 1: R1 & R4 remediation (backend security, async, db ping, telemetry, ruff, ci, dockerignore)
- Worker 2: R2 remediation (frontend React Bits refactor, cleanup custom UI & shadcn)
- Worker 3: R3 remediation (core engine algorithmic defects)

### Phase 2: Verification, Review & Adversarial Stress Testing
- 2 Reviewers (Backend/Core & Frontend/CI)
- 2 Challengers (Algorithmic edge cases & async/API performance)
- Forensic Auditor (teamwork_preview_auditor) for integrity verification

### Phase 3: Final Acceptance Gate & Post-Victory Reporting
- Validate all acceptance criteria:
  - CORS no wildcard credentials
  - CPU-bound operations use asyncio.to_thread
  - /health/ready SELECT 1 DB ping
  - React Bits exclusive UI in Next.js without shadcn/ui
  - Dinic source==sink returns 0.0
  - Bitmask TSP does not duplicate start node
  - Marketplace multi-headcount respected
  - Tree reduction zero-padding identity preserved
  - Ruff check passes with zero errors
  - .dockerignore present and correct
  - CI pinned trivy-action
- Forensic Auditor CLEAN attestation
- Report victory to parent
