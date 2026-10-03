# Project: Production-Grade Resume & Job Matching Talent Marketplace Engine

## Architecture

A production-grade talent marketplace and algorithmic matching platform featuring a **Zero-Library Algorithmic Core (DSA-3 Modules M1–M6)**, an asynchronous **FastAPI** backend with **PostgreSQL + pgvector**, **Sentence-Transformers** semantic embeddings, and a dark-mode-first **Next.js** TypeScript web dashboard.

### Core Architectural Layers
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Next.js Frontend Dashboard                         │
│  - Candidate Portal: Drag-and-drop parser, profile cards, job diagnostics   │
│  - Recruiter Portal: Requisition posting, Dinic allocation, min-cut bottlenecks│
│  - Visualizations: Pure-SVG radar charts, ATS score gauges, breakdown bars  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / JSON / SSE (RFC 7807)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            FastAPI REST API Boundary                        │
│  - Controllers: Resumes, Jobs, Matches, Adhoc, Marketplace Allocation       │
│  - Middleware: CORS, RFC 7807 Exception Handlers, Telemetry (Prometheus)    │
│  - Schemas: Pydantic v2 validation models                                   │
└───────────────────┬─────────────────────────────────────┬───────────────────┘
                    │                                     │
┌───────────────────▼─────────────────────┐ ┌─────────────▼───────────────────┐
│       Core Parsers & Integrations       │ │    Zero-Library Algorithmic     │
│  - Text Extraction: PDF, DOCX, TXT      │ │             Engine              │
│  - Public APIs: Arbeitnow, RandomUser,  │ │  - M1: Custom Data Structures   │
│    PurgoMalum, Datamuse, Nominatim      │ │  - M2: String Matching (Aho-Cor)│
│  - SentenceTransformers (384d vectors)  │ │  - M3: Advanced DP (NW, SW, WF) │
└───────────────────┬─────────────────────┘ │  - M4: Network Flow (Dinic)     │
                    │                       │  - M5: Approximation (Set Cover)│
                    │                       │  - M6: Randomized & Parallel    │
                    │                       └─────────────┬───────────────────┘
┌───────────────────▼─────────────────────────────────────▼───────────────────┐
│                    PostgreSQL + pgvector Data Layer                         │
│  - Tables: candidates, resumes, job_postings, skills, match_results         │
│  - HNSW vector index: vector_cosine_ops                                     │
│  - Alembic async migrations                                                 │
│  - Realistic seeder: 20+ jobs, 40+ candidates                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cardinal Constraint: Zero-Library Core
Inside `core/engine/*`, all standard library collection utilities are **strictly forbidden** (`collections`, `heapq`, `bisect`, `networkx`, etc.). Every structure and algorithm is built from primitive arrays and reference pointers. Monitored and enforced by a pre-commit scanner and automated forensic audits.

---

## Feature Inventory

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | Custom Data Structures | CustomArrayList, CustomLinkedList, CustomHashMap, CustomPriorityQueue (4-ary heap), CustomAdjacencyGraph | M1 | DSA Update M1 |
| F02 | String Matching Algorithms | KMPMatcher, ZAlgorithm, RabinKarp, SuffixArray + KasaiLCP | M1 | DSA Update M2 |
| F03 | Aho-Corasick Skill Automaton | Trie with BFS failure links & dictionary links for O(N+M) scanning of 20,000+ skills | M1 | DSA Update M2 |
| F04 | Advanced Dynamic Programming | WagnerFischer (Levenshtein + Damerau + weighted), SequenceAlignment (Needleman-Wunsch & Smith-Waterman) | M1 | DSA Update M3 |
| F05 | Combinatorial & Tree DP | BitmaskTSP (recruiter route), SOSDynamicProgramming (skill density), TreeRerootingDP (org centroids) | M1 | DSA Update M3 |
| F06 | Network Flow Engine | EdmondsKarp, DinicAlgorithm (level graph + blocking flow), MarketplaceFlowNetwork, MinCutAnalyzer, MinCostMaxFlow | M1 | DSA Update M4 |
| F07 | Approximation Algorithms | GreedySetCover (1+ln n team builder), VertexCoverApproximation (2-approx), KnapsackFPTAS (budget hiring) | M1 | DSA Update M5 |
| F08 | Randomized & Parallel Primitives | ReservoirSampler (Algorithm R), MillerRabin, ParallelPrimitives (Blelloch scan & reduction) | M1 | DSA Update M6 |
| F09 | Import Integrity Enforcement | Pre-commit hook & static test verifying zero forbidden imports in `core/engine/` | M1 | DSA Update Constraint |
| F10 | Database Models & Schema | Candidates, Resumes (Vector(384)), JobPostings (Vector(384)), Skills, MatchResults | M2 | R1, Survey Backend |
| F11 | Alembic Migrations | Async Alembic environment with pgvector extension initialization & HNSW indexes | M2 | R1, AC Infrastructure |
| F12 | Realistic Data Seeder | Database seeder generating 20+ job requisitions and 40+ diverse candidate profiles | M2 | R1, Scope Update |
| F13 | Public API Enrichment Layer | Arbeitnow (live tech jobs), RandomUser (profiles), PurgoMalum (profanity sanitizer), Datamuse, Nominatim | M2 | Enhancement Update |
| F14 | Multi-Format Resume Parser | Pure-Python PDF, DOCX, and TXT parsing with magic byte verification and sanitization | M3 | R1, AC Backend |
| F15 | Embedding Generation Service | SentenceTransformers (`all-MiniLM-L6-v2`) with deterministic offline fallback | M3 | R2, Survey Backend |
| F16 | Algorithmic Entity Extractor | Skill extraction via Aho-Corasick, experience via regex/date parsing, education via ordinal rank, contact info | M3 | R2, DSA Update |
| F17 | Hybrid ATS Scoring Engine | 4-signal weighted score: 40% semantic, 35% skills, 15% experience, 10% education with full zero-division guards | M3 | R2, AC Matching |
| F18 | ATS Explainability & Diagnostics | Matched skills, missing skills (required/preferred), per-signal breakdown, actionable improvement suggestions | M3 | R2, AC Matching |
| F19 | Resume Upload REST API | `POST /api/v1/resumes/upload` accepts file, validates, parses, embeds, stores in DB, returns parsed profile | M4 | R1, AC Backend |
| F20 | Job Posting CRUD & Search API | `POST /api/v1/jobs`, `GET /api/v1/jobs` with pagination, keyword search, location filtering | M4 | R1, AC Backend |
| F21 | Ranked Candidate Matches API | `GET /api/v1/jobs/{id}/matches` returns candidates ranked by hybrid ATS score with full explainability | M4 | R1, AC Backend |
| F22 | Ad-hoc Match REST API | `POST /api/v1/match/adhoc` accepts raw resume text and job description, returns instant match breakdown | M4 | R1, AC Backend |
| F23 | Marketplace Flow & Optimization API | `POST /api/v1/marketplace/allocate`, `/bottlenecks`, `/team-builder` executing Dinic, Min-Cut, Set Cover | M4 | DSA Update Endpoints |
| F24 | Operational Health Checks | `GET /health/live` and `GET /health/ready` verifying database connection and model readiness | M4 | R1, AC Backend |
| F25 | RFC 7807 Problem Details | Global exception handler returning standard application/problem+json error responses | M4 | R1, AC Backend |
| F26 | Candidate Portal Web UI | Drag-and-drop uploader with validation, parsed profile view, ATS match diagnostic cards, score breakdown | M5 | R3, AC Frontend |
| F27 | Recruiter Portal Web UI | Job creation form, job requisition listings, talent matching trigger, candidate leaderboard, skill gap UI | M5 | R3, AC Frontend |
| F28 | Bespoke SVG Data Visualizations | Pure-SVG radial score gauge, 4-point ATS radar chart, comparative skill breakdown bars (zero dependencies) | M5 | R3, Survey Frontend |
| F29 | Responsive Dark-Mode-First UI | Modern Tailwind CSS layout, responsive design, zero console errors | M5 | R3, AC Frontend |
| F30 | Empirical Big-O Benchmarks | Benchmark suite in `tests/benchmarks/` validating Dinic vs Edmonds-Karp, Aho-Corasick linear scale, SOS DP | M6 | DSA Update Tests |
| F31 | Formal Work-Span Analysis | `docs/architecture/work_span_analysis.md` (T_1, T_infinity, Brent's theorem proofs for parallel scan) | M6 | DSA Update Docs |
| F32 | Architecture Decision Records | ADR 0001 (Zero-library core), 0002 (Dinic flow), 0003 (Aho-Corasick), 0004 (Set cover approximation) | M6 | DSA Update Docs |
| F33 | Docker Compose Orchestration | Multi-container setup for backend, frontend, PostgreSQL/pgvector with health checks | M6 | R4, AC Infrastructure |
| F34 | CI/CD Pipeline & Tooling Config | GitHub Actions workflow, Ruff linting/formatting, Biome check for TypeScript, lefthook hook | M6 | R4, AC Infrastructure |
| F35 | Repository Governance | README.md with architecture overview and quickstart, .env.example, .gitignore | M6 | R4, AC Infrastructure |
| F36 | Opaque-Box E2E Test Suite | Independent 4-Tier test suite (Tiers 1-4) verifying all features end-to-end | M-E2E | Project Pattern Dual Track |
| F37 | Adversarial Hardening (Tier 5) | Challenger-driven boundary stress testing, mutation testing, zero-division penetration | M7 | Project Pattern Phase 2 |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M-E2E | Requirement-Driven Opaque-Box E2E Test Suite | Test runner, Tiers 1-4 test cases (>=11*N + max(5, N/2)), publish TEST_READY.md | none | IN_PROGRESS |
| M1 | Zero-Library Algorithmic Core (DSA-3 M1–M6) | Custom structures, string, DP, flow, approx, randomized, import linter | none | IN_PROGRESS |
| M2 | Database & Data Layer | PostgreSQL+pgvector models, Alembic migrations, 20+ jobs / 40+ candidates seeder, public API enrichment | none | PLANNED |
| M3 | ML/NLP Engine & Parsers | PDF/DOCX/TXT parsers, SentenceTransformers, Aho-Corasick extractor, hybrid ATS scoring, explainability | M1, M2 | PLANNED |
| M4 | Backend REST API & Marketplace Controllers | FastAPI routes (resumes, jobs, matches, adhoc, marketplace), RFC 7807 errors, health probes | M1, M2, M3 | PLANNED |
| M5 | Frontend Web Dashboard | Next.js App Router, TypeScript, Tailwind CSS dark-mode, Candidate portal, Recruiter portal, SVG visualizers | M4 | PLANNED |
| M6 | Final Integration, Benchmarks, Docs & E2E Pass | 100% pass on E2E test suite (Tiers 1-4), benchmarks, work_span_analysis.md, ADRs 0001-0004, Docker, CI | M-E2E, M5 | PLANNED |
| M7 | Adversarial Hardening (Tier 5) & Final Audit | Challenger loop for boundary hardening, forensic integrity audit (clean veto check) | M6 | PLANNED |

---

## Interface Contracts

### 1. `core/engine/structures` ↔ `core/engine/string`, `dp`, `flow`
- `CustomArrayList[T]`:
  - `append(item: T) -> None` [Amortized O(1)]
  - `get(index: int) -> T` [O(1)]
  - `set(index: int, item: T) -> None` [O(1)]
  - `size() -> int`
- `CustomHashMap[K, V]`:
  - `put(key: K, value: V) -> None` [Average O(1)]
  - `get(key: K, default: V = None) -> V` [Average O(1)]
  - `contains(key: K) -> bool`
  - `keys() -> CustomArrayList[K]`
- `CustomPriorityQueue[T]` (Min/Max 4-ary heap):
  - `push(priority: float, item: T) -> None` [O(log4 n)]
  - `pop() -> Tuple[float, T]` [O(log4 n)]
  - `peek() -> Tuple[float, T]` [O(1)]
- `CustomAdjacencyGraph`:
  - `add_node(node_id: int) -> None`
  - `add_edge(u: int, v: int, capacity: float, cost: float = 0.0) -> None`
  - `get_residual_capacity(u: int, v: int) -> float`

### 2. `core/engine/flow/DinicAlgorithm` ↔ `api/controllers/marketplace`
- `execute_allocation(candidates: List[CandidateNode], jobs: List[JobNode], capacities: Dict[int, int]) -> AllocationResult`:
  - Computes max flow using level graph BFS and blocking flow DFS.
  - Returns `AllocationResult(total_matches=int, assignments=List[Assignment(candidate_id, job_id, score)])`.
- `find_bottlenecks(network: MarketplaceFlowNetwork) -> BottleneckReport`:
  - Min s-t cut analysis on residual graph.
  - Returns `BottleneckReport(saturated_edges=List[Edge], cut_capacity=float, bottleneck_skills=List[str])`.

### 3. `core/engine/approx/GreedySetCover` ↔ `api/controllers/marketplace`
- `find_minimum_team(candidates: List[CandidateSkillProfile], target_skills: Set[str]) -> TeamCoverResult`:
  - Returns minimal subset of candidates covering all target skills with (1 + ln n) approximation bound.

### 4. `core/engine/matcher` ↔ `api/controllers` & `schemas`
- `calculate_hybrid_score(candidate: ParsedProfile, job: JobRequisition) -> MatchScoreBreakdown`:
  - Formula: `total = 100 * (0.40 * semantic + 0.35 * skill + 0.15 * experience + 0.10 * education)`.
  - Returns:
    ```python
    MatchScoreBreakdown(
        total_score: float,       # 0.0 to 100.0
        semantic_score: float,    # 0.0 to 1.0 (raw & weighted)
        skill_score: float,       # 0.0 to 1.0
        experience_score: float,  # 0.0 to 1.0
        education_score: float,   # 0.0 to 1.0
        matched_skills: List[str],
        missing_skills: List[str],
        improvement_suggestions: List[str]
    )
    ```

### 5. `api/controllers` ↔ `frontend`
- Base URL: `/api/v1`
- `POST /api/v1/resumes/upload` -> `200 OK` `ParsedResumeProfile` | `400/415/422` `ProblemDetails`
- `POST /api/v1/jobs` -> `201 Created` `JobResponse`
- `GET /api/v1/jobs` -> `200 OK` `PaginatedJobResponse`
- `GET /api/v1/jobs/{id}/matches` -> `200 OK` `RankedMatchResponse`
- `POST /api/v1/match/adhoc` -> `200 OK` `AdHocMatchResponse`
- `POST /api/v1/marketplace/allocate` -> `200 OK` `AllocationResponse`
- `POST /api/v1/marketplace/bottlenecks` -> `200 OK` `BottleneckResponse`
- `POST /api/v1/marketplace/team-builder` -> `200 OK` `TeamBuilderResponse`
- `GET /health/live` & `GET /health/ready` -> `200 OK` / `503 Service Unavailable`
- Errors: `application/problem+json` (`type`, `title`, `status`, `detail`, `instance`)

---

## Code Layout

```
.
├── core/
│   ├── engine/                        # STRICT ZERO-LIBRARY ZONE (NO collections/heapq/bisect/networkx)
│   │   ├── structures/                # CustomArrayList, CustomHashMap, CustomPriorityQueue, CustomLinkedList, CustomAdjacencyGraph
│   │   ├── string/                    # KMP, Z-Algorithm, Rabin-Karp, Aho-Corasick automaton, SuffixArray + Kasai LCP
│   │   ├── dp/                        # Wagner-Fischer, Needleman-Wunsch, Smith-Waterman, Bitmask TSP, SOS DP, Tree Rerooting DP
│   │   ├── flow/                      # Dinic's Algorithm, Edmonds-Karp, Min-Cut, Min-Cost Max-Flow (SSP)
│   │   ├── approx/                    # Greedy Set Cover (1+ln n), 2-Approx Vertex Cover, Knapsack FPTAS
│   │   └── randomised/                # Reservoir Sampling (Algorithm R), Miller-Rabin, Blelloch Parallel Scan
│   └── parsers/                       # PDF, DOCX, TXT document parser & entity extractor (libraries allowed here)
├── api/
│   ├── controllers/                   # FastAPI endpoint routers (resumes, jobs, matches, adhoc, marketplace, health)
│   ├── schemas/                       # Pydantic v2 data contracts & RFC 7807 problem details
│   └── telemetry/                     # Prometheus metrics & logging
├── db/
│   ├── models/                        # SQLAlchemy ORM models (Candidates, Resumes, Jobs, Skills, MatchResults)
│   ├── migrations/                    # Alembic environment & versioned migrations with pgvector
│   └── seed/                          # Realistic data generator (20+ jobs, 40+ candidates, live Arbeitnow/RandomUser)
├── src/
│   └── integrations/                  # Optional Public API enrichment layer (Arbeitnow, RandomUser, PurgoMalum, Datamuse, Nominatim)
├── frontend/                          # Next.js App Router, TypeScript, Tailwind CSS dark-mode dashboard
│   ├── app/                           # layout.tsx, page.tsx, candidate/page.tsx, recruiter/page.tsx
│   ├── components/                    # Pure-SVG gauge, radar chart, skill gap visualizer, upload zone
│   └── lib/                           # Typed API client with problem details handling
├── tests/
│   ├── unit/                          # Zero-library data structures, algorithms, scoring formulas, parsers
│   ├── integration/                   # Database operations, FastAPI endpoints, public API fallbacks
│   ├── benchmarks/                    # Empirical Big-O verification (Dinic vs EK, Aho-Corasick, SOS DP)
│   └── e2e/                           # Requirement-driven opaque-box test runner (Tiers 1-4)
├── docs/
│   ├── architecture/
│   │   └── work_span_analysis.md      # Formal work-span proofs (T_1, T_infinity, Brent's theorem)
│   └── adr/                           # 0001-zero-library-core, 0002-dinic-flow, 0003-aho-corasick, 0004-set-cover
├── docker-compose.yml                 # Orchestration for backend, frontend, PostgreSQL/pgvector with healthchecks
├── Dockerfile                         # Backend container specification
├── lefthook.yml                       # Pre-commit hook enforcing zero-library constraint in core/engine/
├── ruff.toml                          # Python linting & formatting rules
├── biome.json                         # TypeScript linting & formatting rules
└── .github/
    └── workflows/
        └── ci.yml                     # Multi-stage CI pipeline (lint, test, security, build)
```
