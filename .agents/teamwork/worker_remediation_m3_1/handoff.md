# Handoff Report: Milestone 3 — Core Engine Defects Remediation

## 1. Observation

### 1.1 Dinic Source == Sink Loop Guard (`core/engine/flow/dinic.py`)
- **File & Lines**: `core/engine/flow/dinic.py:16-20`
- **Verbatim Code**:
  ```python
  @classmethod
  def compute_max_flow(cls, graph: CustomAdjacencyGraph, source: int, sink: int) -> float:
      """Compute maximum flow from source to sink in O(V^2 * E) time."""
      if source == sink:
          return 0.0
      total_flow = 0.0
  ```
- **Observed Behavior**:
  When `source == sink`, lines 18–19 immediately return `0.0`. This prevents `bfs_level_graph()` from marking `level[sink] >= 0` and `dfs_blocking_flow()` from returning `float("inf")` in an infinite augmentation loop.
- **Verification Command & Result**:
  `uv run pytest tests/benchmarks/test_challenger_m1_stress.py -k test_bug3_dinic_source_equal_sink_infinite_loop` -> `1 passed in 0.22s`.

### 1.2 Bitmask TSP Tour Non-duplication (`core/engine/dp/bitmask_tsp.py`)
- **File & Lines**: `core/engine/dp/bitmask_tsp.py:68-80`
- **Verbatim Code**:
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
  return (best_cost, path)
  ```
- **Observed Behavior**:
  The tour reconstruction initializes `path = [start_node]`, traverses back to `curr_node = start_node`, and appends `start_node`. Reversing creates a closed tour `[start_node, v_1, ..., v_{n-1}, start_node]` of length exactly $N+1$. No trailing redundant node is appended.
- **Verification Command & Result**:
  `uv run pytest tests/benchmarks/test_challenger_m1_stress.py -k test_bug2_bitmask_tsp_duplicate_start_node_in_tour` -> `1 passed in 0.23s`.
  `uv run pytest tests/stress/test_m1_empirical_stress.py -k test_bitmask_tsp_tour_reconstruction_integrity` -> `1 passed in 0.25s`.

### 1.3 Marketplace Multi-Headcount & Job Capacity Resolution (`core/engine/flow/marketplace_network.py` & `api/controllers/marketplace.py`)
- **File & Lines**: `core/engine/flow/marketplace_network.py:42-54, 70-85, 129-180`
- **Modifications**:
  1. Updated `JobNode.__init__` to accept `headcount: int | None = None` in addition to `capacity: int = 1`, storing both `self.capacity` and `self.headcount`:
     ```python
     class JobNode:
         def __init__(
             self,
             job_id: Any,
             required_skills: list[str] | None = None,
             capacity: int = 1,
             headcount: int | None = None,
         ) -> None:
             self.job_id = job_id
             self.required_skills = required_skills or []
             self.capacity = headcount if headcount is not None else capacity
             self.headcount = self.capacity
     ```
  2. Implemented `MarketplaceFlowNetwork._resolve_job_capacity(j)`:
     ```python
     @staticmethod
     def _resolve_job_capacity(j: Any) -> int:
         if hasattr(j, "headcount") and getattr(j, "headcount", None) is not None:
             return getattr(j, "headcount")
         if hasattr(j, "capacity") and getattr(j, "capacity", None) is not None:
             return getattr(j, "capacity")
         if hasattr(j, "get"):
             val = j.get("headcount")
             if val is not None:
                 return val
             return j.get("capacity", 1)
         return 1
     ```
  3. Added attribute & dictionary key fallback for candidate IDs (`candidate_id` or `id`) and job IDs (`job_id` or `id`), as well as adding `build_flow_network = build_network` alias.
  4. In `api/controllers/marketplace.py`, wired `/allocate`, `/bottlenecks`, and `/team-builder` to `MarketplaceFlowNetwork` (Dinic's Algorithm), `MinCutAnalyzer`, and `GreedySetCover`. Added request models supporting optional input payloads and sensible defaults (`SAMPLE_CANDIDATES` and `SAMPLE_JOBS`).
- **Verification Commands & Results**:
  `uv run pytest tests/benchmarks/test_challenger_m1_stress.py -k test_bug1_marketplace_network_job_capacity_omission` -> `1 passed in 0.24s`.
  `uv run pytest tests/unit/test_engine_flow.py -k test_marketplace_capacity_constraints` -> `1 passed in 0.08s`.
  `uv run pytest tests/e2e/test_tier1_features.py -k test_f23_marketplace_allocation_api` -> `1 passed in 0.12s`.

### 1.4 Tree Reduction Identity Preservation (`core/engine/randomised/parallel_primitives.py`)
- **File & Lines**: `core/engine/randomised/parallel_primitives.py:118-137`
- **Modifications**:
  Updated `tree_reduce` signature to accept optional `identity: float | int | None = None`. Handled empty input data (`n == 0`) by returning `identity if identity is not None else 0`:
  ```python
  @classmethod
  def tree_reduce(
      cls,
      data: Sequence[float | int],
      op: Callable[[float | int, float | int], float | int] = lambda x, y: x + y,
      identity: float | int | None = None,
  ) -> ReductionResult:
      """Tree-based parallel reduction with O(N) work and O(log N) span."""
      n = len(data)
      if n == 0:
          default_val = identity if identity is not None else 0
          return ReductionResult(
              value=default_val,
              metrics=ParallelMetrics(work=0, span=0, parallelism=1.0),
          )
      if n == 1:
          return ReductionResult(
              value=data[0],
              metrics=ParallelMetrics(work=0, span=0, parallelism=1.0),
          )
  ```
  Verified that non-empty array reduction carries unpaired elements forward without zero-padding, ensuring non-additive operators (min, max, multiplication) preserve mathematical correctness.
- **Verification Command & Result**:
  `uv run pytest tests/stress/test_m1_empirical_stress.py -k test_parallel_primitives_tree_reduce_non_zero_identity` -> `1 passed in 0.25s`.

### 1.5 Strict Zero-Library Constraint Enforcement
- **File**: `tests/unit/test_forbidden_imports.py`
- **AST Scan**: Verified all 16 python files in `core/engine/` contain zero forbidden imports (`collections`, `heapq`, `bisect`, `networkx`, `queue`, `array`, `sortedcontainers`, `scipy`, `numpy`, `pandas`, `igraph`).
- **Result**: `2 passed in 0.06s`.

---

## 2. Logic Chain

1. **Dinic source==sink infinite loop**:
   - *Observation*: Dinic's algorithm initializes `level[source] = 0`. If `source == sink`, BFS marks sink reached, and DFS with base condition `u == sink` returns `inf`, causing `total_flow += inf` in an infinite loop.
   - *Logic*: An $O(1)$ guard `if source == sink: return 0.0` at line 18 circumvents BFS/DFS execution entirely and returns the true flow of 0.0.
   - *Conclusion*: Confirmed and verified.

2. **Bitmask TSP tour reconstruction**:
   - *Observation*: Reconstructing the tour by pushing `start_node` initially and backtracking to `curr_node == start_node` naturally places `start_node` at the start and end of the reversed array.
   - *Logic*: Omitting any extra `path.append(start_node)` prevents tour elongation to $N+2$. The tour length is exactly $N+1$ without duplicate start nodes.
   - *Conclusion*: Confirmed and verified.

3. **Multi-headcount capacity resolution**:
   - *Observation*: `JobPosting` and API schemas define `headcount: int = 1`, while `JobNode` previously only accepted `capacity`. When models or API payloads without `capacity` were passed, capacity defaulted to 1.
   - *Logic*: Updating `JobNode` to accept `headcount` and implementing `_resolve_job_capacity` to check `headcount` then `capacity` on both object attributes and dictionary keys ensures multi-headcount postings (e.g. 2, 3, 5 openings) allocate up to their full quota.
   - *Conclusion*: Flow conservation and multi-headcount allocations work properly.

4. **Tree reduction monoid identity**:
   - *Observation*: In an algebraic monoid $(S, \oplus, I)$, non-additive operators have non-zero identities ($I=-\infty$ for max, $I=+\infty$ for min, $I=1$ for product).
   - *Logic*: Adding `identity` parameter and returning it for empty inputs prevents arbitrary zero returns. For non-empty inputs, avoiding zero-padding by carrying odd elements forward ensures non-additive reductions produce exact results.
   - *Conclusion*: Confirmed and verified.

---

## 3. Caveats

- In `api/controllers/marketplace.py`, `/allocate` and `/bottlenecks` fall back to `SAMPLE_CANDIDATES` and `SAMPLE_JOBS` when called without a request body. When explicit candidates and jobs are provided in the payload, those provided entities are used.
- `tests/contract/test_openapi.py::test_health_contracts_schemathesis[GET /health/ready]` fails with HTTP 503 only when a local PostgreSQL server is not running (which is handled by worker remediation M1). All marketplace and OpenAPI schema validation tests pass.

---

## 4. Conclusion

All requirements for Milestone 3 (Core Engine Defects Remediation) have been implemented and verified:
1. `core/engine/flow/dinic.py` returns 0.0 when source == sink without entering BFS/DFS loops.
2. `core/engine/dp/bitmask_tsp.py` produces an exact $N+1$ closed tour without duplicate start nodes.
3. `core/engine/flow/marketplace_network.py` respects `headcount` and `capacity`, and `api/controllers/marketplace.py` routes `/allocate`, `/bottlenecks`, and `/team-builder` through the core algorithmic engines.
4. `core/engine/randomised/parallel_primitives.py` tree reduction handles `identity` correctly and preserves monoid invariants.
5. Strict zero-library constraint is fully maintained across all `core/engine/` modules.

---

## 5. Verification Method

To independently reproduce and verify:

1. **Verify Unit Tests (including forbidden imports)**:
   ```powershell
   uv run pytest tests/unit/
   ```
   *Expected output*: `73 passed`.

2. **Verify Stress Tests**:
   ```powershell
   uv run pytest tests/stress/
   ```
   *Expected output*: `56 passed`.

3. **Verify Benchmark & Challenger Bug Tests**:
   ```powershell
   uv run pytest tests/benchmarks/
   ```
   *Expected output*: `20 passed`.

4. **Verify E2E Tests**:
   ```powershell
   uv run pytest tests/e2e/
   ```
   *Expected output*: `90 passed`.

5. **Verify Zero Forbidden Imports AST Scan**:
   ```powershell
   uv run pytest tests/unit/test_forbidden_imports.py -v
   ```
   *Expected output*: `2 passed`.

6. **Verify Ruff Lint on Modified Files**:
   ```powershell
   uv run ruff check core/engine/flow/marketplace_network.py core/engine/randomised/parallel_primitives.py api/controllers/marketplace.py
   ```
   *Expected output*: `All checks passed!`.
