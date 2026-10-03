# Handoff Report: Empirical Stress-Testing for Milestone 1 (Zero-Library Algorithmic Core)

**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

Empirical stress testing of Milestone 1 (`core/engine/dp`, `core/engine/approx`, `core/engine/randomised`) was executed via custom stress harness and oracles in `tests/stress/test_m1_empirical_stress.py`.

Execution command:
```powershell
python -m pytest tests/stress/test_m1_empirical_stress.py -v
```
Result: **21 passed, 2 failed** in 0.92s.

### Defect 1 (Severity: HIGH) — `BitmaskTSP.find_optimal_tour` Tour Reconstruction Corruption
- **File**: `core/engine/dp/bitmask_tsp.py`, lines 71–83
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
  path.append(start_node)
  return (best_cost, path)
  ```
- **Empirical Execution**:
  ```powershell
  python -c "from core.engine.dp.bitmask_tsp import BitmaskTSP; m = [[0, 5], [5, 0]]; print(BitmaskTSP.find_optimal_tour(m, 0))"
  ```
  **Output**: `(10.0, [0, 1, 0, 0])` (Length 4 for 2 cities; duplicate adjacent `0` at end).
  For $N=4$ cities: `[0, 2, 3, 1, 0, 0]` (Length 6 instead of 5).
  For $N=12$ cities: `[0, 5, 6, 10, 3, 2, 1, 8, 4, 11, 9, 7, 0, 0]` (Length 14 instead of 13).
- **Test Failure**:
  ```
  FAILED tests/stress/test_m1_empirical_stress.py::test_bitmask_tsp_tour_reconstruction_integrity
  AssertionError: DEFECT REPRODUCED: BitmaskTSP.find_optimal_tour returned tour of length 6 for 4 cities: [0, 2, 3, 1, 0, 0]. Expected length 5.
  assert 6 == (4 + 1)
  ```
- **Why worker test missed it**: `tests/unit/test_engine_dp.py:85-86` only asserted `tour[0] == 0 and tour[-1] == 0` and `len(set(tour[:-1])) == 4`, masking the adjacent duplicate `0` at `tour[-2]` and `tour[-1]`.

---

### Defect 2 (Severity: MEDIUM) — `ParallelPrimitives.tree_reduce` Identity Element Corruption on Non-Power-of-Two Lengths
- **File**: `core/engine/randomised/parallel_primitives.py`, lines 136–154
- **Verbatim Code**:
  ```python
  m = cls._next_power_of_two(n)
  a: list[float | int] = [0] * m
  for i in range(n):
      a[i] = data[i]
  ```
- **Empirical Execution**:
  ```powershell
  python -c "from core.engine.randomised.parallel_primitives import ParallelPrimitives; res = ParallelPrimitives.tree_reduce([-10, -20, -30], op=max); print('Result:', res.value)"
  ```
  **Output**: `Result: 0` (Expected `-10`).
  ```powershell
  python -c "from core.engine.randomised.parallel_primitives import ParallelPrimitives; res = ParallelPrimitives.tree_reduce([10, 20, 30], op=min); print('Result:', res.value)"
  ```
  **Output**: `Result: 0` (Expected `10`).
- **Test Failure**:
  ```
  FAILED tests/stress/test_m1_empirical_stress.py::test_parallel_primitives_tree_reduce_non_zero_identity
  AssertionError: DEFECT REPRODUCED: ParallelPrimitives.tree_reduce returned 0 instead of -10. Buffer was padded with 0, which is not the identity for max.
  assert 0 == -10
  ```
- **Root Cause**: The buffer is hardcoded with `0` padding. $0$ is the identity for addition, but corrupts operations where the identity is $-\infty$ (`max`), $+\infty$ (`min`), $1$ (`mul`), or non-trivial monoids.

---

### Defect 3 (Severity: LOW / Code Smell) — `WagnerFischer.DEFAULT_DOMAIN_SUBSTITUTIONS` Dead Digraph Keys
- **File**: `core/engine/dp/wagner_fischer.py`, lines 24–25 and 129–136
- **Observation**:
  `DEFAULT_DOMAIN_SUBSTITUTIONS` defines `("ph", "f"): 0.5` and `("f", "ph"): 0.5`. However, in `domain_weighted_distance`:
  ```python
  c1 = s1[i - 1].lower()
  c2 = s2[j - 1].lower()
  current_sub = sub_map.get((c1, c2), sub_cost)
  ```
  `c1` and `c2` are single-character substrings (`len == 1`). Therefore, `(c1, c2)` can never equal `("ph", "f")`. This mapping is dead code and never activates.

---

### Passing Stress Checks Verified
All other focus areas passed rigorous mathematical, empirical, and statistical validation:
1. **WagnerFischer**: Levenshtein, Damerau-Levenshtein, and domain-weighted distances handle empty strings, single characters, completely disjoint strings, and satisfy metric axioms (identity, symmetry, triangle inequality).
2. **SequenceAlignment**: Needleman-Wunsch & Smith-Waterman handle empty strings, single characters, completely disjoint strings, and correctly isolate local high-scoring regions (`_PYTHON_ENGINEER_`, score 51.0, identity rate 1.0).
3. **BitmaskTSP $N=12$ Performance**: Solved in $0.014$s ($< 0.5$s requirement). Open Hamiltonian path correctly reconstructs $N$ vertices.
4. **SOSDynamicProgramming $N=10$ Mask Density**: 1024/1024 masks strictly match independent brute-force submask enumeration and superset enumeration. `SkillDensityIndex` passed all candidate query scenarios.
5. **TreeRerootingDP**: All-node distance sums match an independent BFS oracle with $0.0$ difference across Path Graph ($N=20$), Star Graph ($N=30$), Balanced Binary Tree ($N=31$), and non-uniform headcounts. Centroids correctly identified.
6. **GreedySetCover**: 100% of 50 test instances adhere to the $(1 + \ln |U|) \cdot \text{OPT}$ approximation bound against an exact branch-and-bound oracle.
7. **VertexCoverApproximation**: 100% of 50 test instances produce valid covers satisfying $|C| \le 2 \cdot \text{OPT}$ against an exact bitmask oracle.
8. **KnapsackFPTAS**: 100% of 50 test instances adhere to $\text{total\_value} \ge (1 - \epsilon) \cdot \text{OPT}$ and respect budget limits against an exact knapsack oracle.
9. **ReservoirSampler Uniformity**: Pearson Chi-Square goodness-of-fit test ($N=20, k=5, M=20,000$ trials) yielded $\chi^2 = 17.85$ (critical threshold $36.19$ for $\alpha=0.01$, $\text{df}=19$), validating uniform streaming sampling.
10. **MillerRabin**: 100% agreement with prime sieve on all integers up to 5,000; all Carmichael pseudoprimes correctly rejected as composite; all Mersenne primes up to $2^{127}-1$ verified.
11. **ParallelPrimitives Blelloch Scan**: Exclusive and inclusive prefix sums match serial sums across all array sizes and distributions; work-span metrics adhere to theoretical guarantees ($T_1 = 3(M-1), T_\infty = 2 \log_2 M$).

---

## 2. Logic Chain

1. **Observation 1** establishes that `BitmaskTSP.find_optimal_tour` returns a tour of length $N+2$ containing adjacent duplicate start vertices (`[start, ..., start, start]`).
2. By graph definition, a Hamiltonian tour in TSP must visit each of the $N$ vertices once and return to the start node, spanning exactly $N$ edges and $N+1$ vertex visits ($v_0 \to v_1 \to \dots \to v_{n-1} \to v_0$).
3. The presence of an extra start node introduces a spurious zero-length self-loop edge $(v_0, v_0)$ and causes length-checking assertions and downstream edge iteration to fail.
4. **Observation 2** establishes that `ParallelPrimitives.tree_reduce` pads input arrays to the nearest power of 2 with zero (`[0] * m`).
5. For monoids where zero is not the neutral identity element (e.g. `max` over negative values where identity is $-\infty$, or `min` over positive values where identity is $+\infty$), zero becomes an active participant in reduction, overriding valid array elements and returning false answers.
6. Therefore, the implementation in `core/engine/` contains functional defects that violate algorithmic correctness and interface integrity.

---

## 3. Caveats

- `core/engine/structures/` and `core/engine/string/` were evaluated in parallel by peer agent `challenger_m1_1` and were not tested in this harness beyond import integrity.
- All empirical benchmarks were conducted in Python 3.13 on Windows x64.
- No production files were edited (strictly adhering to the review-only constraint).

---

## 4. Conclusion

**Verdict: REQUEST_CHANGES**

Milestone 1 is well-architected and 90%+ compliant, but cannot be approved until the following two bugs are remediated by the worker:

1. **Fix `BitmaskTSP.find_optimal_tour` in `core/engine/dp/bitmask_tsp.py:71-83`**:
   Change line 71:
   ```python
   # Replace:
   path: list[int] = [start_node]
   # With:
   path: list[int] = []
   ```
   Or adjust the reversal and append sequence so that the final tour has length $N+1$ without duplicate adjacent start nodes.

2. **Fix `ParallelPrimitives.tree_reduce` in `core/engine/randomised/parallel_primitives.py:136-154`**:
   Avoid corrupting non-additive operators by either:
   - Initializing the padding with an optional `identity` parameter, OR
   - Iteratively reducing the active slice `data` in-place/pairwise without power-of-two zero-padding.

3. **(Optional cleanup) `WagnerFischer` in `core/engine/dp/wagner_fischer.py:24-25`**:
   Remove or update the multi-character entries `("ph", "f")` from `DEFAULT_DOMAIN_SUBSTITUTIONS` as single-character lookups never match them.

---

## 5. Verification Method

1. Run the empirical stress test suite:
   ```powershell
   python -m pytest tests/stress/test_m1_empirical_stress.py -v
   ```
2. Verify existing unit tests remain green:
   ```powershell
   python -m pytest tests/unit/ -v
   ```
3. Invalidation conditions:
   - Any failure in `test_bitmask_tsp_tour_reconstruction_integrity` (tour length $\ne N+1$ or duplicate adjacent start nodes).
   - Any failure in `test_parallel_primitives_tree_reduce_non_zero_identity` (`tree_reduce` returning incorrect values for `max`/`min` reductions on non-power-of-2 arrays).
