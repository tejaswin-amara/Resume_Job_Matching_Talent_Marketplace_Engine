## 2026-09-29T08:35:00Z

You are worker_m1_core_1.
Your working directory is: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_m1_core_1

MANDATORY: You MUST read ORIGINAL_REQUEST.md at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md

Also read PROJECT.md at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

CARDINAL CONSTRAINT (CRITICAL):
Inside `core/engine/*`, ALL standard library collection utilities are STRICTLY FORBIDDEN.
NO `collections`, NO `heapq`, NO `bisect`, NO `networkx`, or equivalents.
Every data structure and algorithm must be built from primitive arrays and reference pointers.

Your mission (Milestone 1 — Zero-Library Algorithmic Core):
Implement the 6 DSA modules inside `core/engine/`:
1. `core/engine/structures/`:
   - `CustomArrayList`: Resizable array with geometric amortized O(1) append
   - `CustomLinkedList`: Doubly linked list with O(1) head/tail operations
   - `CustomHashMap`: Chaining hash table with polynomial rolling hash, resize at load factor >= 0.75
   - `CustomPriorityQueue`: Min/Max 4-ary heap with O(log4 n) insert/extract
   - `CustomAdjacencyGraph`: Graph with forward and residual edges for network flow
2. `core/engine/string/`:
   - `KMPMatcher`: KMP failure table + search in O(N+M)
   - `ZAlgorithm`: Z-array construction + pattern search
   - `RabinKarp`: Dual-prime rolling hash for plagiarism/duplicate detection
   - `AhoCorasickAutomaton`: Trie + BFS failure links + dictionary output links for scanning 20,000+ skills in O(N+M)
   - `SuffixArray` + `KasaiLCP`: O(n log² n) suffix array + O(n) LCP
3. `core/engine/dp/`:
   - `WagnerFischer`: Levenshtein + Damerau-Levenshtein + domain-weighted edit distance for fuzzy skill normalization
   - `SequenceAlignment`: Needleman-Wunsch (global) + Smith-Waterman (local) with gap scoring for career trajectory alignment
   - `BitmaskTSP`: O(2^n * n^2) optimal recruiter interview route
   - `SOSDynamicProgramming`: Sum-Over-Subsets via Yates' technique for instant skill mask density queries
   - `TreeRerootingDP`: Find organizational centroids and balance departmental headcounts
4. `core/engine/flow/`:
   - `EdmondsKarp`: BFS-based max flow O(V E^2)
   - `DinicAlgorithm`: Level graph BFS + blocking flow DFS with edge pruning O(V^2 E)
   - `MarketplaceFlowNetwork`: Source -> Candidates -> Jobs -> Sink with capacity constraints
   - `MinCutAnalyzer`: Compute min s-t cut from residual network for bottleneck analysis
   - `MinCostMaxFlow`: Successive Shortest Path with cycle cancellation
5. `core/engine/approx/`:
   - `GreedySetCover`: (1 + ln n) approximation for minimal team competency formation
   - `VertexCoverApproximation`: 2-approx via maximal matching for conflict resolution
   - `KnapsackFPTAS`: Budget-constrained hiring optimization
6. `core/engine/randomised/`:
   - `ReservoirSampler`: Algorithm R for unbiased streaming applicant sampling
   - `MillerRabin`: Primality testing + universal hash families for tamper-proof credentials
   - `ParallelPrimitives`: Blelloch work-efficient parallel prefix-scan + tree-based parallel reduction
7. Import scanner & pre-commit hook:
   - Create `lefthook.yml` and a test script `tests/unit/test_forbidden_imports.py` that parses AST of all files in `core/engine/` and asserts ZERO forbidden imports.
8. Unit tests in `tests/unit/test_engine_*.py`:
   - Exhaustive tests verifying algorithmic correctness, edge cases, and performance of every data structure and algorithm.
   - Run tests using `pytest` and verify 100% pass.

Your Exclusive File Ownership:
`core/engine/**`, `tests/unit/test_engine_*.py`, `tests/unit/test_forbidden_imports.py`, `lefthook.yml`

Write your comprehensive report and test results to:
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_m1_core_1\handoff.md`.

Update progress.md in your directory.
Send a concise message to the orchestrator when finished.
