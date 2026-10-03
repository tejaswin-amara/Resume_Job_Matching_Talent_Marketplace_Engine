"""SOSDynamicProgramming: Sum-Over-Subsets via Yates' technique in O(n * 2^n) time.

Used for instant talent marketplace skill mask density queries and candidate availability counting.
Zero-library constraint: built strictly with primitive arrays and bitwise manipulation.
"""

from collections.abc import Sequence


class SOSDynamicProgramming:
    """Sum-Over-Subsets (SOS) DP using Yates' technique."""

    @staticmethod
    def compute_subsets_sum(values: Sequence[float | int], num_bits: int) -> list[float | int]:
        """Compute F[mask] = sum_{sub in mask} values[sub] for all masks in O(n * 2^n)."""
        size = 1 << num_bits
        dp = list(values[:size])
        if len(dp) < size:
            dp.extend([0] * (size - len(dp)))

        for i in range(num_bits):
            bit = 1 << i
            for mask in range(size):
                if mask & bit:
                    dp[mask] += dp[mask ^ bit]

        return dp

    @staticmethod
    def compute_supersets_sum(values: Sequence[float | int], num_bits: int) -> list[float | int]:
        """Compute G[mask] = sum_{mask in sup} values[sup] for all masks in O(n * 2^n).

        Answers: count of entities possessing at least all skills in `mask`.
        """
        size = 1 << num_bits
        dp = list(values[:size])
        if len(dp) < size:
            dp.extend([0] * (size - len(dp)))

        for i in range(num_bits):
            bit = 1 << i
            for mask in range(size - 1, -1, -1):
                if not (mask & bit):
                    dp[mask] += dp[mask | bit]

        return dp


class SkillDensityIndex:
    """Instant O(1) query index for candidate skill bitmasks via Yates' SOS DP."""

    def __init__(self, num_skills: int) -> None:
        self.num_skills: int = num_skills
        self.table_size: int = 1 << num_skills
        self._counts: list[int] = [0] * self.table_size
        self._superset_dp: list[int] = []
        self._subset_dp: list[int] = []
        self._is_indexed: bool = False

    def add_candidate_mask(self, mask: int) -> None:
        """Register a candidate's skill bitmask."""
        if 0 <= mask < self.table_size:
            self._counts[mask] += 1
            self._is_indexed = False

    def build_index(self) -> None:
        """Run Yates' SOS DP to precompute subset and superset densities in O(n * 2^n)."""
        self._subset_dp = SOSDynamicProgramming.compute_subsets_sum(self._counts, self.num_skills)  # type: ignore
        self._superset_dp = SOSDynamicProgramming.compute_supersets_sum(
            self._counts, self.num_skills
        )  # type: ignore
        self._is_indexed = True

    def count_candidates_with_all_skills(self, required_mask: int) -> int:
        """Count candidates possessing at least all skills in required_mask in O(1) time."""
        if not self._is_indexed:
            self.build_index()
        if 0 <= required_mask < self.table_size:
            return self._superset_dp[required_mask]
        return 0

    def count_candidates_with_subset_of_skills(self, allowable_mask: int) -> int:
        """Count candidates whose skills are a subset of allowable_mask in O(1) time."""
        if not self._is_indexed:
            self.build_index()
        if 0 <= allowable_mask < self.table_size:
            return self._subset_dp[allowable_mask]
        return 0
