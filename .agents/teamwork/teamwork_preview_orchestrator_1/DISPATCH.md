# Dispatch Log

## 2026-09-29T08:26:46Z

You are the Project Orchestrator (teamwork_preview_orchestrator).

Your working directory is:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_orchestrator_1

Your mission is defined verbatim in ORIGINAL_REQUEST.md at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md

Mission Summary:
Build a production-grade Resume & Job Matching Talent Marketplace Engine — a full-stack platform with FastAPI backend, Next.js frontend, PostgreSQL+pgvector storage, and a hybrid ML scoring engine that combines semantic vector similarity, skill matching, experience alignment, and education fit to rank candidates against job postings with ATS-style explainability.

Requirements & Acceptance Criteria:
- R1. Backend API & Data Layer (FastAPI, PostgreSQL+pgvector, Alembic migrations, seed script, REST endpoints, upload/parse, job CRUD, match endpoints, health checks)
- R2. ML/NLP Matching Engine (Hybrid scoring engine 40% semantic, 35% skills, 15% experience, 10% education; resume parsing with entity extraction, explainability output)
- R3. Frontend Dashboard (Next.js/React TypeScript, candidate portal, recruiter portal, dark-mode-first, Tailwind CSS)
- R4. Infrastructure & Quality (Docker Compose orchestration with health checks, comprehensive test suite with maximized coverage, ruff linting for Python, biome for TypeScript, GitHub Actions CI workflow, README with architecture & quick start, .env.example, .gitignore)

Guidelines:
1. Maintain your BRIEFING.md, plan.md, and progress.md in your working directory.
2. Coordinate and dispatch specialists as needed to implement and verify all requirements.
3. Keep progress.md regularly updated with concrete milestone achievements and evidence.
4. When all requirements and acceptance criteria are fully satisfied, tested, and verified, report completion back to the Sentinel.

## 2026-09-29T08:31:22Z

## Enhancement Request: Public API Integrations

The user wants the project enhanced with integrations from https://github.com/public-apis/public-apis. Here are the curated APIs to integrate as an **optional enrichment layer** at `src/integrations/`:

### Priority 1 — Include in MVP:
1. **Arbeitnow API** (`https://www.arbeitnow.com/api`) — Free, no auth. Use to seed the database with REAL tech job postings instead of purely synthetic data. Create a fetcher in the seed script that pulls live jobs.
2. **RandomUser API** (`https://randomuser.me/api/`) — Free, no auth. Use to generate realistic candidate profiles (names, emails, photos, locations) for the seed data script.
3. **PurgoMalum API** (`http://www.purgomalum.com/service/json?text=`) — Free, no auth. Add as an input sanitization layer for resume text and job descriptions to filter profanity.

### Priority 2 — Add if time permits:
4. **Datamuse API** (`https://api.datamuse.com/words?ml=`) — Free, no auth. Use for skill synonym expansion in the skill taxonomy (e.g., "JS" → "JavaScript", "k8s" → "Kubernetes").
5. **Nominatim/OpenStreetMap** (`https://nominatim.openstreetmap.org/`) — Free, no auth. Parse and geocode job/candidate locations for potential location-based matching.

### Implementation guidelines:
- All external API calls must be **optional** — the app works without them
- Use **environment variables** for any API keys  
- Add **timeout handling** (3-5 second timeouts)
- **Cache responses** to respect rate limits
- Create integration module at `src/integrations/` with separate files per concern

This is an additive enhancement, not a core requirement change. Prioritize completing the core matching engine and API first.

## 2026-09-29T08:32:16Z

## 🚨 CRITICAL SCOPE UPDATE — Zero-Library Algorithmic Core + DSA-3 Module Requirements

The project scope has been significantly expanded. The original 4-requirement spec is now augmented with a **mandatory zero-library algorithmic engine** based on a DSA-3 course specification (25CS2103E, Modules M1–M6). This is NOT optional — it's a hard constraint.

### New Cardinal Constraint
**Inside `core/engine/*`, ALL standard library collection utilities are FORBIDDEN.** No `collections`, `heapq`, `bisect`, `networkx`, or equivalent. Every data structure and algorithm must be built from primitive arrays and reference pointers. Modern frameworks (FastAPI, SQLAlchemy, Pydantic, React) are permitted ONLY at the outer I/O boundary.

### New Directory Structure
The `src/` directory should be restructured to use `core/` and `api/` at root level:
```
core/
├── engine/                    # ZERO STDLIB IMPORTS ZONE
│   ├── structures/            # CustomArrayList, CustomHashMap, CustomPriorityQueue, CustomLinkedList, CustomAdjacencyGraph
│   ├── string/                # KMP, Z-Algorithm, Rabin-Karp, Aho-Corasick automaton, SuffixArray + Kasai LCP
│   ├── dp/                    # Wagner-Fischer, Needleman-Wunsch, Smith-Waterman, Bitmask TSP, SOS DP, Tree Rerooting DP
│   ├── flow/                  # Dinic's Algorithm, Edmonds-Karp, Min-Cut, Min-Cost Max-Flow (SSP)
│   ├── approx/                # Greedy Set Cover (1+ln n), 2-Approx Vertex Cover, Knapsack FPTAS
│   └── randomised/            # Reservoir Sampling (Algorithm R), Miller-Rabin, Blelloch Parallel Scan
└── parsers/                   # PDF/DOCX/Text extraction (libraries allowed here)
api/
├── controllers/               # FastAPI routes
├── schemas/                   # Pydantic models
└── telemetry/                 # OpenTelemetry + Prometheus
db/
├── models/                    # SQLAlchemy models
├── migrations/                # Alembic
└── seed/                      # Seed data (20+ jobs, 40+ candidates now)
```

### 6 DSA Modules to Implement (ALL REQUIRED)

**M1 - Custom Data Structures (`core/engine/structures/`):**
- `CustomArrayList`: Resizable array with geometric amortized O(1) append
- `CustomLinkedList`: Doubly linked list with O(1) head/tail ops
- `CustomHashMap`: Chaining hash table with polynomial rolling hash, resize at load factor ≥ 0.75
- `CustomPriorityQueue`: Min/Max 4-ary heap with O(log n) insert/extract
- `CustomAdjacencyGraph`: Graph with forward + residual edges for network flow

**M2 - String Algorithms (`core/engine/string/`):**
- `KMPMatcher`: KMP failure table + search in O(N+M)
- `ZAlgorithm`: Z-array construction + pattern search
- `RabinKarp`: Dual-prime rolling hash for plagiarism/duplicate detection
- `AhoCorasickAutomaton`: Trie + BFS failure links + dictionary output links — used to scan 20,000+ skill terms against resume text in ONE linear pass
- `SuffixArray` + `KasaiLCP`: O(n log²n) suffix array + O(n) LCP for experience pattern analysis

**M3 - Advanced DP (`core/engine/dp/`):**
- `WagnerFischer`: Levenshtein + Damerau-Levenshtein + domain-weighted edit distance for fuzzy skill normalization
- `SequenceAlignment`: Needleman-Wunsch (global) + Smith-Waterman (local) with gap scoring for career trajectory alignment
- `BitmaskTSP`: O(2^n · n²) optimal recruiter interview route
- `SOSDynamicProgramming`: Sum-Over-Subsets via Yates' technique for instant skill mask density queries
- `TreeRerootingDP`: Find organizational centroids and balance departmental headcounts

**M4 - Network Flow (`core/engine/flow/`):**
- `EdmondsKarp`: BFS-based max flow O(VE²)
- `DinicAlgorithm`: Level graph BFS + blocking flow DFS with edge pruning O(V²E)
- `MarketplaceFlowNetwork`: Source→Candidates→Jobs→Sink with capacity constraints
- `MinCutAnalyzer`: Compute min s-t cut from residual network for bottleneck analysis
- `MinCostMaxFlow`: Successive Shortest Path with cycle cancellation

**M5 - Approximation (`core/engine/approx/`):**
- `GreedySetCover`: (1+ln n) approximation for minimal team competency formation
- `VertexCoverApproximation`: 2-approx via maximal matching for conflict resolution
- `KnapsackFPTAS`: Budget-constrained hiring optimization

**M6 - Randomized & Parallel (`core/engine/randomised/`):**
- `ReservoirSampler`: Algorithm R for unbiased streaming applicant sampling
- `MillerRabin`: Primality testing + universal hash families for tamper-proof credentials
- `ParallelPrimitives`: Blelloch work-efficient parallel prefix-scan + tree-based parallel reduction

### New API Endpoints (in addition to existing ones)
- `POST /api/v1/marketplace/allocate` — Execute Dinic's algorithm for optimal global candidate-job assignment
- `POST /api/v1/marketplace/bottlenecks` — Run Min-Cut to find talent pipeline bottlenecks
- `POST /api/v1/marketplace/team-builder` — Execute Greedy Set Cover for minimum team covering all skills

### Updated Hybrid Scoring Engine
The scoring engine should now USE the DSA algorithms:
- **Skill extraction**: Aho-Corasick automaton (not simple set matching)
- **Fuzzy skill matching**: Wagner-Fischer edit distance
- **Experience alignment**: Smith-Waterman sequence alignment
- Same formula: S_ATS = 100 × (0.40·S_sem + 0.35·S_skill + 0.15·S_align + 0.10·S_edu)

### New Test Categories
- `tests/benchmarks/` — Empirical Big-O verification:
  - Confirm Dinic's scales O(V²E) and outperforms Edmonds-Karp on dense graphs
  - Confirm Aho-Corasick and KMP scale linearly O(N+M)
  - Confirm SOS DP executes in O(n·2^n)
- Increase seed data to 20+ jobs and 40+ candidates

### New Documentation
- `docs/architecture/work_span_analysis.md` — Formal work-span proofs (T_1, T_∞, Brent's theorem) for parallel primitives
- New ADRs: `0001-zero-library-core.md`, `0002-dinic-flow-assignment.md`, `0003-aho-corasick-taxonomy.md`, `0004-set-cover-approximation.md`

### Enforcement
Add a pre-commit hook in `lefthook.yml` that scans `core/engine/` for forbidden imports (collections, heapq, bisect, networkx, etc.) and fails the commit if found.

This is a MAJOR expansion. Reprioritize accordingly — the algorithmic core is the centerpiece. Frontend and CI are secondary to getting the algorithms correct and tested.

## 2026-09-29T08:33:59Z

## Supplementary API Integrations — High-Value Additions from Full Research

After reviewing the complete public-apis repository, here are additional high-value free APIs specifically for the talent marketplace. These supplement the Priority 1-3 list I sent earlier.

### Jobs Feed APIs (Direct Marketplace Value)
These can populate the marketplace with REAL job data:
1. **freehire** (`https://freehire.dev/docs/api`) — Free, no auth. Open-source tech job aggregator from company ATS boards. Perfect for seeding real job postings.
2. **Artificial Intelligence Jobs** (`https://artificialintelligencejobs.co/developers`) — Free, no auth. Live AI/ML job listings from 260+ companies with salary, location, remote and seniority filters.
3. **RemoteOK** (`https://remoteok.com/api`) — Free, no auth. Remote job board, simple JSON API.
4. **GraphQL Jobs** (`https://graphql.jobs/docs/api/`) — Free, no auth. Dev/engineering jobs via GraphQL.

### Email Validation (Free, No Auth)
For validating extracted candidate email addresses:
5. **EVA** (`https://eva.pingutil.com/`) — Free, no auth. Email validation.
6. **Disify** (`https://www.disify.com/`) — Free, no auth. Detect disposable/temporary emails.
7. **MailCheck.ai** (`https://www.mailcheck.ai/#documentation`) — Free, no auth. Block temp email signups.

### Text/NLP Enhancement
8. **Jina AI** (`https://jina.ai`) — Free tier with apiKey. Embeddings and reranking API — could serve as a fallback/alternative embedding provider if sentence-transformers is too heavy for deployment.
9. **Voxell Forge** (`https://voxell.ai/docs/#forge`) — Free-forever text embeddings API, OpenAI-compatible. Another embedding alternative.

### Test Data for Realistic Seeding
10. **This Person Does Not Exist** (`https://thispersondoesnotexist.com`) — Free, no auth. Generate realistic avatar photos for candidate profiles in the dashboard.
11. **Mockaroo** (`https://www.mockaroo.com/docs`) — Free tier. Generate fake structured data (names, emails, addresses, job titles) in JSON/CSV format.

### Integration Priority
- Use **freehire + Arbeitnow + RemoteOK** in the seed script to populate with real jobs
- Use **EVA + Disify** for email validation in the resume parsing pipeline  
- Use **RandomUser + This Person Does Not Exist** for realistic seed candidate profiles
- Consider **Jina AI** as a lightweight cloud embedding alternative to local sentence-transformers

Same rules: all integrations optional, env vars for keys, timeout handling, cached responses.
