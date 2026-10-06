# Dispatch: Challenger 1 (Algorithmic Core Stress Verification)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_algorithmic_core_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Worker Handoff Report
- Worker 3 (M3): `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m3_1\handoff.md`

## Challenge Scope & Instructions
Perform adversarial stress testing on core engine algorithms and boundary conditions:
1. **Dinic source == sink**:
   - Verify `DinicAlgorithm.compute_max_flow(g, s, s)` returns `0.0` immediately without hanging or infinite looping on various graph sizes (0 nodes, 1 node, dense graph).
2. **Bitmask TSP Tour**:
   - Verify `BitmaskTSP.find_optimal_tour` on matrices of various sizes (1, 2, 3, 4, 10 nodes).
   - Ensure the tour starts and ends at the origin and does NOT have adjacent duplicate start nodes (exact length $N+1$).
3. **Marketplace Multi-Headcount Flow**:
   - Test `MarketplaceFlowNetwork` with jobs having `headcount > 1` (e.g. 2, 3, 5 openings) and candidate pools exceeding capacity, verifying that capacity is fully respected and not clamped to 1.
4. **Tree Reduction Identity**:
   - Stress test `ParallelPrimitives.tree_reduce` with empty lists and various associative operators (addition with identity 0, multiplication with identity 1, min with identity float("inf"), max with identity float("-inf")).
   - Verify that odd-sized lists and boundary sizes do not introduce spurious zero elements into non-additive operators.
5. **Zero-Library Constraint**:
   - Validate that NO module in `core/engine/` imports `collections`, `heapq`, `bisect`, `networkx`, `queue`, `array`, `sortedcontainers`, `scipy`, `numpy`.

Run tests:
- `uv run pytest tests/stress/`
- `uv run pytest tests/benchmarks/`
- `uv run pytest tests/unit/test_forbidden_imports.py`

Deliver your verdict (`APPROVE` or `REQUEST_CHANGES`) with empirical results in `handoff.md`.

## 2026-10-06T04:06:03Z
You are a Challenger subagent for the Resume & Job Matching Talent Marketplace Engine project.
Your identity: challenger_algorithmic_core_1
Your working directory: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_algorithmic_core_1

MANDATORY FIRST STEP: Read the authoritative user request at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md
Also read your assignment at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_algorithmic_core_1\DISPATCH.md
And the worker handoff at:
- `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m3_1\handoff.md`

Adversarially test the core engine algorithms:
- Dinic source == sink: verify returns 0.0 immediately without infinite looping.
- Bitmask TSP tour: verify exact N+1 closed tour length and no duplicated start node.
- Marketplace flow network: verify multi-headcount job postings allocate up to capacity.
- Tree reduction: verify optional identity parameter and monoid identity preservation on empty and odd-sized lists for non-additive operators (min, max, multiplication).
- Strict zero-library constraint in `core/engine/`.
Run tests:
- `uv run pytest tests/stress/`
- `uv run pytest tests/benchmarks/`
- `uv run pytest tests/unit/test_forbidden_imports.py`
Write your findings and verdict (APPROVE or REQUEST_CHANGES) to:
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\challenger_algorithmic_core_1\handoff.md`
and notify me via send_message when complete.
