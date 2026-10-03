"""KnapsackFPTAS: Fully Polynomial-Time Approximation Scheme for 0-1 Knapsack.

Provides provable (1 - epsilon) approximation for budget-constrained talent hiring.
Runtime complexity: O(n^2 / epsilon).
Zero-library constraint: built strictly with primitive DP arrays and pointer reconstruction.
"""

from typing import Sequence
from typing import Any, NamedTuple


class HiringCandidate(NamedTuple):
    """Candidate representation for budget-constrained knapsack hiring."""

    candidate_id: Any
    cost: float  # Weight (salary/cost)
    value: float  # Value (score / qualification points)


class KnapsackResult(NamedTuple):
    """Result of FPTAS knapsack optimization."""

    selected_candidates: list[HiringCandidate]
    total_cost: float
    total_value: float
    epsilon: float
    approximation_ratio: float


class KnapsackFPTAS:
    """Fully Polynomial-Time Approximation Scheme for 0-1 Knapsack."""

    @classmethod
    def solve(
        cls,
        candidates: Sequence[HiringCandidate],
        budget: float,
        epsilon: float = 0.1,
    ) -> KnapsackResult:
        """Find candidate subset with total cost <= budget and total value >= (1 - epsilon) * OPT.

        Time complexity: O(n^2 / epsilon).
        """
        if not candidates or budget <= 0 or epsilon <= 0:
            return KnapsackResult([], 0.0, 0.0, epsilon, 1.0 - epsilon)

        # Filter out candidates whose individual cost exceeds budget
        valid_candidates = [c for c in candidates if c.cost <= budget and c.value > 0]
        n = len(valid_candidates)
        if n == 0:
            return KnapsackResult([], 0.0, 0.0, epsilon, 1.0 - epsilon)

        v_max = max(c.value for c in valid_candidates)
        if v_max <= 0:
            return KnapsackResult([], 0.0, 0.0, epsilon, 1.0 - epsilon)

        # Scaling factor K
        k_factor = (epsilon * v_max) / float(n)
        if k_factor <= 0:
            k_factor = 1.0

        # Scaled values
        scaled_values = [int(c.value / k_factor) for c in valid_candidates]
        max_possible_scaled_val = sum(scaled_values)

        if max_possible_scaled_val == 0:
            # Just take the first valid candidate
            c = valid_candidates[0]
            return KnapsackResult([c], c.cost, c.value, epsilon, 1.0 - epsilon)

        # dp[v] = minimum weight to achieve scaled value v
        inf = float("inf")
        dp: list[float] = [inf] * (max_possible_scaled_val + 1)
        dp[0] = 0.0

        # Backtrack matrix: chosen[i][v] = True if candidate i was included
        chosen: list[list[bool]] = [[False] * (max_possible_scaled_val + 1) for _ in range(n)]

        for i in range(n):
            w = valid_candidates[i].cost
            sv = scaled_values[i]
            for v in range(max_possible_scaled_val, sv - 1, -1):
                if dp[v - sv] + w < dp[v]:
                    dp[v] = dp[v - sv] + w
                    chosen[i][v] = True

        # Find maximum scaled value with cost <= budget
        best_v = 0
        for v in range(max_possible_scaled_val, -1, -1):
            if dp[v] <= budget:
                best_v = v
                break

        # Reconstruct selected candidates
        selected: list[HiringCandidate] = []
        curr_v = best_v
        for i in range(n - 1, -1, -1):
            if chosen[i][curr_v]:
                selected.append(valid_candidates[i])
                curr_v -= scaled_values[i]

        selected.reverse()
        total_cost = sum(c.cost for c in selected)
        total_value = sum(c.value for c in selected)

        return KnapsackResult(
            selected_candidates=selected,
            total_cost=total_cost,
            total_value=total_value,
            epsilon=epsilon,
            approximation_ratio=1.0 - epsilon,
        )
