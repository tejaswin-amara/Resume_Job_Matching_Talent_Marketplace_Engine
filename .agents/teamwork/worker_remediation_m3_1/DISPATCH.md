# Dispatch: Worker M3 (Core Engine Defects Remediation)

## Working Directory
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\worker_remediation_m3_1`

## Authoritative Reference
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`

## Explorer Investigation Report
`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_r3_1\handoff.md`

## Scope & File Ownership
You exclusively own and modify:
- `core/engine/flow/dinic.py`
- `core/engine/dp/bitmask_tsp.py`
- `core/engine/flow/marketplace_network.py`
- `core/engine/randomised/parallel_primitives.py`
- `api/controllers/marketplace.py`

## Objectives
1. **Dinic source==sink infinite loop (`core/engine/flow/dinic.py`)**:
   - Verify lines 18-19 in `DinicAlgorithm.compute_max_flow`:
     `if source == sink: return 0.0`
   - Ensure that when `source == sink`, it returns `0.0` immediately without entering BFS/DFS loops.
2. **Bitmask TSP Tour Non-duplication (`core/engine/dp/bitmask_tsp.py`)**:
   - Verify tour reconstruction in `BitmaskTSP.find_optimal_tour`:
     Ensure the closed tour length is exactly $N+1$ and the start node is not duplicated at the end (no `[start, ..., start, start]`).
3. **Marketplace Job Capacity & Multi-Headcount (`core/engine/flow/marketplace_network.py` & `api/controllers/marketplace.py`)**:
   - Update `JobNode` in `core/engine/flow/marketplace_network.py` to accept `capacity: int = 1` or `headcount: int | None = None` (mapping headcount to capacity).
   - In `MarketplaceFlowNetwork.execute_allocation` (and `build_flow_network`), resolve job capacity using:
     `job_cap = getattr(j, "headcount", getattr(j, "capacity", j.get("headcount", j.get("capacity", 1))))`
     so that multi-headcount job postings (e.g. 3, 5 openings) are properly modeled in the flow network.
   - In `api/controllers/marketplace.py`, wire up the `/allocate` and `/bottlenecks` endpoints to `MarketplaceFlowNetwork` so Dinic's algorithm is invoked and multi-headcount allocations work end-to-end.
4. **Tree Reduction Zero-Padding Identity Violation (`core/engine/randomised/parallel_primitives.py`)**:
   - Inspect `ParallelPrimitives.tree_reduce`.
   - Add optional `identity: float | int | None = None` parameter.
   - For empty data `n == 0`, if `identity is not None` return `ReductionResult(value=identity, ...)`; otherwise for default addition return `0`.
   - When reducing with arbitrary operators, ensure no artificial 0 element corrupts non-additive reductions (e.g. min, max, multiplication).
5. **Verify zero-library constraint**:
   - CRITICAL: DO NOT import standard library collections (`collections`, `heapq`, `bisect`, `networkx`, etc.) inside `core/engine/`. All implementations must adhere strictly to the zero-library constraint!

## Verification Required
- Run `uv run pytest tests/unit/` (including `test_forbidden_imports.py`).
- Run `uv run pytest tests/stress/`.
- Run `uv run pytest tests/benchmarks/`.
- Document all test outcomes in `handoff.md`.
