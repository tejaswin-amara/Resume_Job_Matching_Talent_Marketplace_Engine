# Gate Status Tracker

## Gate — Milestone 1 (Zero-Library Algorithmic Core) — Iteration 1
| Agent | Role | Verdict | Source |
|---|---|---|---|
| worker_m1_core_1 | teamwork_preview_worker | DONE | worker_m1_core_1/handoff.md |
| reviewer_m1_1 | teamwork_preview_reviewer | REQUEST_CHANGES | reviewer_m1_1/handoff.md |
| reviewer_m1_2 | teamwork_preview_reviewer | REQUEST_CHANGES | reviewer_m1_2/handoff.md |
| challenger_m1_1 | teamwork_preview_challenger | REQUEST_CHANGES | challenger_m1_1/handoff.md |
| challenger_m1_2 | teamwork_preview_challenger | REQUEST_CHANGES | challenger_m1_2/handoff.md |
| auditor_m1_1 | teamwork_preview_auditor | CLEAN | auditor_m1_1/handoff.md |

Gate Result: **FAIL** (Reviewers and Challengers requested changes on 4 surgical edge cases)

### Action Items for Iteration 2:
1. `DinicAlgorithm` & `EdmondsKarp` (`core/engine/flow/dinic.py` & `edmonds_karp.py`):
   - Add guard at start of `compute_max_flow`: `if source == sink: return 0.0`.
2. `MarketplaceFlowNetwork` (`core/engine/flow/marketplace_network.py`):
   - In `build_network`: When `capacities` argument is None or missing `jid`, fall back to `job.capacity` (not hardcoded 1.0):
     `j_cap = capacities.get(jid, job.capacity) if capacities else job.capacity`.
3. `BitmaskTSP.find_optimal_tour` (`core/engine/dp/bitmask_tsp.py`):
   - Remove the duplicate double-append of `start_node` so the tour returns a valid cycle of length N+1 `[start, ..., start]`.
4. `ParallelPrimitives.tree_reduce` (`core/engine/randomised/parallel_primitives.py`):
   - Avoid zero-padding with 0 for non-additive reductions; either use identity element or reduce odd elements without altering non-zero values.
