# Milestone 1 Remediation Iteration 2 — Handoff Report

## 1. Observation

Direct observations from initial test executions prior to remediation:
1. `tests/benchmarks/test_challenger_m1_stress.py` failed 3 tests:
   - `TestAlgorithmicBugReproductions.test_bug1_marketplace_network_job_capacity_omission`:
     ```
     AssertionError: BUG 1 REPRODUCED: JobNode.capacity=2 ignored by MarketplaceFlowNetwork! Allocated 1 candidate instead of 2. Fix: save j_cap in build_network and reference it in line 115.
     ```
   - `TestAlgorithmicBugReproductions.test_bug2_bitmask_tsp_duplicate_start_node_in_tour`:
     ```
     AssertionError: BUG 2 REPRODUCED: BitmaskTSP tour contains duplicate start_node: [0, 2, 3, 1, 0, 0]. Expected length 5, got length 6. Fix: remove line 82 `path.append(start_node)` in core/engine/dp/bitmask_tsp.py.
     ```
   - `TestAlgorithmicBugReproductions.test_bug3_dinic_source_equal_sink_infinite_loop`:
     ```
     AssertionError: BUG 3 REPRODUCED: DinicAlgorithm hung in infinite loop when source == sink! Fix: Add boundary check at start of compute_max_flow: `if source == sink: return 0.0`.
     ```
2. `tests/stress/test_m1_empirical_stress.py` failed 2 tests:
   - `test_bitmask_tsp_tour_reconstruction_integrity`:
     ```
     AssertionError: DEFECT REPRODUCED: BitmaskTSP.find_optimal_tour returned tour of length 6 for 4 cities: [0, 2, 3, 1, 0, 0]. Expected length 5.
     ```
   - `test_parallel_primitives_tree_reduce_non_zero_identity`:
     ```
     AssertionError: DEFECT REPRODUCED: ParallelPrimitives.tree_reduce returned 0 instead of -10. Buffer was padded with 0, which is not the identity for max.
     ```

## 2. Logic Chain

1. **Fix 1: `source == sink` Boundary Guard in Max Flow Algorithms**
   - In `core/engine/flow/dinic.py` (lines 17-21) and `core/engine/flow/edmonds_karp.py` (lines 16-20), when `source == sink`, BFS immediately marks sink as reached at level 0, leading to infinite loops or invalid flow augmentation.
   - Adding `if source == sink: return 0.0` at the beginning of `compute_max_flow` immediately catches degenerate source-sink equality and returns 0.0 flow in O(1) time without entering BFS or DFS loops.
2. **Fix 2: Honor `JobNode.capacity` in `MarketplaceFlowNetwork`**
   - In `core/engine/flow/marketplace_network.py` (line 115), `build_network` previously defaulted to `j_cap = capacities.get(jid, 1) if capacities else 1`, completely discarding `job.capacity` from the `JobNode` instances when `capacities` was None.
   - Modified `build_network` to extract `job_cap = job.capacity if hasattr(job, "capacity") else job.get("capacity", 1)` and use `j_cap = capacities.get(jid, job_cap) if capacities else job_cap`, ensuring `job.capacity` is preserved.
3. **Fix 3: Tour Reconstruction in `BitmaskTSP.find_optimal_tour`**
   - In `core/engine/dp/bitmask_tsp.py`, backtracking was initialized with `path: list[int] = [start_node]`. The while loop appended predecessors until reaching `start_node`, after which `path.reverse()` yielded the complete closed cycle `[start_node, ..., start_node]` of length N + 1.
   - Line 82 subsequently executed `path.append(start_node)` an extra time, resulting in an invalid length N + 2 path with duplicate adjacent start nodes `[start_node, ..., start_node, start_node]`.
   - Removing `path.append(start_node)` produces the exact Hamiltonian cycle of length N + 1 starting and ending at `start_node`.
4. **Fix 4: Elimination of Zero-Padding in `ParallelPrimitives.tree_reduce`**
   - In `core/engine/randomised/parallel_primitives.py`, `tree_reduce` previously padded input data with zeros up to the next power of 2 (`a = [0] * m`). For non-additive associative operators (e.g. `max` on negative numbers or `min` on positive numbers), 0 is not the identity element, corrupting the reduction result.
   - Refactored `tree_reduce` to perform layer-by-layer pairwise reduction over active elements without padding:
     ```python
     current = list(data)
     work_count = 0
     span_depth = 0
     while len(current) > 1:
         next_level = []
         span_depth += 1
         for i in range(0, len(current), 2):
             if i + 1 < len(current):
                 next_level.append(op(current[i], current[i + 1]))
                 work_count += 1
             else:
                 next_level.append(current[i])
         current = next_level
     ```
   - This ensures correct results for all associative operators on any input size while accurately recording work ($T_1$) and span ($T_\infty$).
5. **Zero-Library Cardinal Constraint Preservation**
   - None of the edits introduced any standard library imports. `tests/unit/test_forbidden_imports.py` was executed and confirmed 100% compliance with zero forbidden imports in `core/engine/`.

## 3. Caveats

No caveats. All four identified edge-case defects have been resolved surgically with zero collateral modifications.

## 4. Conclusion

All 4 remediation items requested by reviewers and challengers have been implemented and verified.
Across the entire test suite:
- Unit tests (`tests/unit/`): 54 passed, 0 failed (100% pass)
- Challenger stress benchmarks (`tests/benchmarks/test_challenger_m1_stress.py`): 16 passed, 0 failed (100% pass)
- Empirical stress tests (`tests/stress/test_m1_empirical_stress.py`): 23 passed, 0 failed (100% pass)
- E2E opaque-box test runner (`tests/e2e/runner.py`): 90 passed, 0 failed (100% pass)
Total: 183 passed tests with zero regressions and full zero-library compliance.

## 5. Verification Method

To independently verify the implementation, execute the following commands in the workspace root:

```bash
# 1. Unit tests
python -m pytest tests/unit/ -v

# 2. Challenger stress benchmark tests
python -m pytest tests/benchmarks/test_challenger_m1_stress.py -v

# 3. Empirical stress tests
python -m pytest tests/stress/test_m1_empirical_stress.py -v

# 4. E2E opaque-box test runner
python tests/e2e/runner.py

# 5. Full test suite pass
python -m pytest tests/ -v
```

Files modified:
- `core/engine/flow/dinic.py`
- `core/engine/flow/edmonds_karp.py`
- `core/engine/flow/marketplace_network.py`
- `core/engine/dp/bitmask_tsp.py`
- `core/engine/randomised/parallel_primitives.py`
