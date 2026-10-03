# Independent Review & Adversarial Challenge Report: Milestone 1 (Zero-Library Algorithmic Core)

**Reviewer Agent**: `reviewer_m1_2`  
**Working Directory**: `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\reviewer_m1_2`  
**Verdict**: **REQUEST_CHANGES**  
**Integrity Audit**: **CLEAN (Zero Integrity Violations Detected)**

---

## 1. Observation

### 1.1 Test Execution Results
The test suites were executed independently in PowerShell:
1. `python -m pytest tests/unit/test_forbidden_imports.py -v`:
   - `test_core_engine_has_zero_forbidden_imports`: **PASSED**
   - `test_import_scanner_detects_violations`: **PASSED**
   - Result: 2 passed in 0.14s (Exit Code: 0).
2. `python -m pytest tests/unit/ -v`:
   - 54 passed in 0.12s (Exit Code: 0).
3. `python tests/e2e/runner.py`:
   - 90 passed in 0.24s (Exit Code: 0).

### 1.2 Cardinal Constraint AST Verification
An exhaustive AST scan of all 24 Python source files in `core/engine/` (`structures/`, `string/`, `dp/`, `flow/`, `approx/`, `randomised/`) confirmed that:
- Prohibited modules (`collections`, `heapq`, `bisect`, `networkx`, `queue`, `array`, `sortedcontainers`, `scipy`, `numpy`, `pandas`, `igraph`) have strictly **0** occurrences.
- Only standard Python primitives, `typing`, `random` (for randomised algorithms), and internal `core.engine.*` modules are imported.
- No dynamic imports (`__import__`, `importlib`, or `sys.modules`) are present.
- `lefthook.yml` correctly targets `python -m pytest tests/unit/test_forbidden_imports.py` on git pre-commit. Note: `ruff check` in `lefthook.yml` requires `ruff` installed in the execution environment.

### 1.3 Discovered Algorithmic Findings

#### [Major] Finding 1: Duplicate `start_node` in `BitmaskTSP.find_optimal_tour`
- **Location**: `core/engine/dp/bitmask_tsp.py:71-84`
- **Observed Code**:
  ```python
  # Reconstruct path backwards
  path: list[int] = [start_node]
  curr_mask = full_mask
  curr_node = last_node

  while curr_node != -1 and curr_mask > 0:
      path.append(curr_node)
      prev_node = parent[curr_mask][curr_node]
      curr_mask ^= 1 << curr_node
      curr_node = prev_node

  path.reverse()
  path.append(start_node)
  return (best_cost, path)
  ```
- **Observed Behavior**:
  For a 4-city cost matrix with `start_node=0`, calling `BitmaskTSP.find_optimal_tour(matrix, start_node=0)` returns:
  `cost: 80.0, tour: [0, 2, 3, 1, 0, 0], length: 6`.
  A valid closed tour on 4 vertices must have 5 entries: `[0, 2, 3, 1, 0]`. The function outputs two trailing zeros (`0 -> 0`).
- **Why It Passed Existing Unit Test**:
  In `tests/unit/test_engine_dp.py:85-86`:
  ```python
  assert tour[0] == 0 and tour[-1] == 0
  assert len(set(tour[:-1])) == 4
  ```
  The unit test checked that the first and last elements were 0, and that `set(tour[:-1])` had 4 unique items. It did not check `len(tour) == n + 1`, masking the duplicate element.
- **Suggested Fix**:
  Either initialize `path: list[int] = []` at line 71 before the while loop, or remove `path.append(start_node)` at line 82.

#### [Major] Finding 2: `JobNode.capacity` Ignored When `capacities` Parameter Is Omitted
- **Location**: `core/engine/flow/marketplace_network.py:101, 114-116`
- **Observed Code**:
  ```python
  # Line 101:
  j_cap = (
      capacities.get(jid, j.capacity if hasattr(j, "capacity") else j.get("capacity", 1))
      if capacities
      else (j.capacity if hasattr(j, "capacity") else j.get("capacity", 1))
  )
  # ... but j_cap is NOT stored on self ...
  # Line 114-116:
  for jid, j_node_id in self.job_map.items():
      j_cap = capacities.get(jid, 1) if capacities else 1
      self.graph.add_edge(j_node_id, self.sink_id, capacity=float(j_cap))
  ```
- **Observed Behavior**:
  When a caller passes `JobNode(job_id="j1", capacity=2)` and calls `net.execute_allocation(candidates, jobs)` without passing the optional `capacities` dictionary, line 115 defaults the capacity of the job-to-sink edge to `1.0`. The candidate capacity `j.capacity` is ignored unless explicitly passed in a redundant dictionary `capacities={"j1": 2}`.
- **Why It Passed Existing Unit Test**:
  `test_marketplace_capacity_constraints` explicitly passed `capacities={"j1": 2}` in the test call, hiding the bug when `capacities` is omitted.
- **Suggested Fix**:
  Store `self.job_capacities: dict[Any, int] = {}` during the job node loop (line 98), and use `self.job_capacities[jid]` at line 115 as the default fallback.

#### [Minor] Finding 3: Tooling Dependency in `lefthook.yml`
- **Location**: `lefthook.yml:9-11`
- **Observed Code**: `run: ruff check core/ tests/`
- **Observed Behavior**: `ruff` is not installed by default in the system Python environment (`No module named ruff`).
- **Suggested Fix**: Add `ruff` to test dependencies or run via `python -m ruff` when available.

---

## 2. Logic Chain

1. *Constraint Check*: `ORIGINAL_REQUEST.md` and `PROJECT.md` define the Cardinal Constraint: strictly zero standard library collection utilities in `core/engine/*`. AST inspection proved zero forbidden imports across all 24 files, satisfying this rule.
2. *Integrity Audit*: Actively checked for hardcoded outputs, empty facades, or bypassed logic. None found: data structures (`CustomArrayList`, `CustomLinkedList`, `CustomHashMap`, `CustomPriorityQueue`, `CustomAdjacencyGraph`) and all algorithms in string, DP, flow, approx, and randomised modules are substantive, fully functional, and compute results dynamically.
3. *Adversarial Stress-Testing*: 8 independent adversarial test suites were executed:
   - `CustomArrayList`: 10,000 element appends and buffer shrinkage upon pop verified.
   - `CustomHashMap`: Heavy collision resolution and non-string keys verified.
   - `CustomPriorityQueue`: 1,000 random floating points verified heap sort invariance.
   - `AhoCorasickAutomaton`: Overlapping multi-pattern search verified.
   - `KMPMatcher`: Periodic strings verified.
   - `DinicAlgorithm` & `EdmondsKarp`: Disconnected graph zero-flow verified.
   - `ParallelPrimitives`: Non-power-of-two Blelloch scans verified.
   - `MillerRabin`: Carmichael composite numbers (561, 1105, 1729, etc.) rejected as primes.
4. *Algorithmic Correctness*: While all 54 unit tests pass, forensic inspection revealed two functional bugs:
   - In `BitmaskTSP.find_optimal_tour`, double-appending `start_node` produces an invalid tour of length $N+2$ instead of $N+1$.
   - In `MarketplaceFlowNetwork.build_network`, `JobNode.capacity` is ignored when `capacities` dict is not supplied.
5. *Verdict Justification*: Although the architectural foundation is excellent and zero-library constraints are fully met, code containing algorithmic bugs in core modules (`BitmaskTSP` and `MarketplaceFlowNetwork`) should not be approved into downstream milestones (M2–M4) without the worker making these two surgical corrections. Hence, `REQUEST_CHANGES`.

---

## 3. Caveats

- `ParallelPrimitives` simulates parallel execution model on single-threaded Python while accurately recording work $T_1$ and span $T_\infty$.
- Downstream M2 (database seeder) and M3 (scoring engine) interface contracts are structurally satisfied and ready to import from `core/engine/` once the two identified fixes are committed.

---

## 4. Conclusion

Milestone 1 is cleanly architected with 100% adherence to the zero-library constraint and zero integrity violations. However, the verdict is **REQUEST_CHANGES** due to two specific algorithmic bugs:
1. `BitmaskTSP.find_optimal_tour` double-appending `start_node` to the tour.
2. `MarketplaceFlowNetwork.build_network` ignoring `JobNode.capacity` when `capacities` is omitted.

Both fixes are surgical (1–2 lines each). Once resolved, Milestone 1 will be ready for immediate approval.

---

## 5. Verification Method

1. **Verify TSP Tour Length**:
   ```powershell
   python -c "from core.engine.dp.bitmask_tsp import BitmaskTSP; m = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]; cost, tour = BitmaskTSP.find_optimal_tour(m, 0); assert len(tour) == 5, f'Expected 5 nodes, got {len(tour)}: {tour}'"
   ```
2. **Verify JobNode Capacity Fallback**:
   ```powershell
   python -c "from core.engine.flow.marketplace_network import MarketplaceFlowNetwork, CandidateNode, JobNode; c = [CandidateNode(f'c{i}', ['python']) for i in range(4)]; j = [JobNode('j1', ['python'], capacity=2)]; net = MarketplaceFlowNetwork(); res = net.execute_allocation(c, j); assert res.total_matches == 2, f'Expected 2 matches, got {res.total_matches}'"
   ```
3. **Verify Zero Forbidden Imports & Test Suites**:
   ```powershell
   python -m pytest tests/unit/test_forbidden_imports.py -v
   python -m pytest tests/unit/ -v
   python tests/e2e/runner.py
   ```
