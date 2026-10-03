## 2026-09-29T08:55:00Z
Task: Milestone 1 — Remediation Iteration 2
Apply the 4 surgical fixes identified by the reviewers and challengers:
1. `core/engine/flow/dinic.py` & `core/engine/flow/edmonds_karp.py`:
   - At the beginning of `compute_max_flow(self, source: int, sink: int)`, add:
     ```python
     if source == sink:
         return 0.0
     ```
2. `core/engine/flow/marketplace_network.py`:
   - In `build_network`, fix line 115 where job capacity was hardcoded to 1 when `capacities` argument is None:
     ```python
     j_cap = capacities.get(jid, job.capacity) if capacities else job.capacity
     ```
     Ensure `job.capacity` is honored when `capacities` is None.
3. `core/engine/dp/bitmask_tsp.py`:
   - In `find_optimal_tour`:
     Line 71 starts `path = [start_node]`, then lines 78-81 reconstruct the path ending back at `start_node`, but line 82 was appending `start_node` an extra time.
     Fix the reconstruction so the tour is a clean cycle of length N+1 starting and ending at `start_node` without duplicate adjacent start nodes (e.g., `[0, 2, 3, 1, 0]`).
4. `core/engine/randomised/parallel_primitives.py`:
   - In `tree_reduce`:
     When length is not a power of 2 or when reducing, do not pad with 0 (which corrupts non-additive operations like `max` of negative numbers). Instead, perform pairwise reduction layer-by-layer on the active elements:
     ```python
     current = list(data)
     while len(current) > 1:
         next_level = []
         for i in range(0, len(current), 2):
             if i + 1 < len(current):
                 next_level.append(op(current[i], current[i + 1]))
             else:
                 next_level.append(current[i])
         current = next_level
     ```
     Verify this handles any associative operator and power/non-power of 2 without corrupting values.

5. Verification:
   - Run `python -m pytest tests/unit/ -v`
   - Run `python -m pytest tests/benchmarks/test_challenger_m1_stress.py -v`
   - Run `python -m pytest tests/stress/test_m1_empirical_stress.py -v`
   - Run `python tests/e2e/runner.py`
   Confirm 100% of tests pass across all suites.
