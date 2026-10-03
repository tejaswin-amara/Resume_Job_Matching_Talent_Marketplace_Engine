# Work-Span Analysis

Formal performance analysis of parallel algorithms utilized in the Zero-Library DSA Engine for batch processing.

## 1. Blelloch Parallel Prefix-Scan
The Blelloch (work-efficient) scan algorithm computes prefix sums, crucial for memory allocation and load balancing in batch scoring.
- **Work ($T_1$):** $O(n)$ operations, maintaining the same complexity as the sequential algorithm.
- **Span ($T_\infty$):** $O(\log n)$ due to the binary tree structure of the up-sweep (reduce) and down-sweep phases.
- **Speedup via Brent's Theorem:** With $p$ processors, the time is bounded by $T_p \le T_1 / p + T_\infty$. For large $n$, $T_p \approx O(n/p + \log n)$. This enables highly efficient batch aggregations.

## 2. Tree-based Parallel Reduction
Used for aggregating scores across multiple matching criteria.
- **Work ($T_1$):** $O(n)$ additions/comparisons.
- **Span ($T_\infty$):** $O(\log n)$ as reductions are performed level-by-level in a tree.

## 3. Practical Implications for Batch Resume Scoring
By leveraging these work-span bounds, the engine can score thousands of resumes against a job description in parallel. The theoretical $O(\log n)$ span ensures that as candidate volume scales, response times remain strictly bounded by available hardware parallelism rather than sequential bottlenecks.
