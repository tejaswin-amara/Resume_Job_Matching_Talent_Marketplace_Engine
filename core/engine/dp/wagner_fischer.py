"""WagnerFischer: Dynamic programming edit distance variants for fuzzy skill normalization.

Includes:
- Levenshtein distance
- Damerau-Levenshtein distance (adjacent transpositions)
- Domain-weighted edit distance (custom typo/keyboard substitution costs)
- Normalized similarity score [0.0, 1.0]

Zero-library constraint: built strictly with 2D primitive DP matrices.
"""


class WagnerFischer:
    """Fuzzy string matching and edit distance engine."""

    # Default phonetic / keyboard substitution discount matrix for tech skills
    DEFAULT_DOMAIN_SUBSTITUTIONS: dict[tuple[str, str], float] = {
        ("c", "k"): 0.4,
        ("k", "c"): 0.4,
        ("s", "z"): 0.4,
        ("z", "s"): 0.4,
        ("ph", "f"): 0.5,
        ("f", "ph"): 0.5,
        ("i", "y"): 0.5,
        ("y", "i"): 0.5,
        ("0", "o"): 0.3,
        ("o", "0"): 0.3,
        ("1", "l"): 0.3,
        ("l", "1"): 0.3,
    }

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Compute standard Levenshtein edit distance in O(N * M) time and O(min(N, M)) space."""
        n = len(s1)
        m = len(s2)

        if n == 0:
            return m
        if m == 0:
            return n

        # Space-optimized two-row DP
        prev_row = list(range(m + 1))
        curr_row = [0] * (m + 1)

        for i in range(1, n + 1):
            curr_row[0] = i
            c1 = s1[i - 1]
            for j in range(1, m + 1):
                c2 = s2[j - 1]
                cost = 0 if c1 == c2 else 1
                curr_row[j] = min(
                    prev_row[j] + 1,  # deletion
                    curr_row[j - 1] + 1,  # insertion
                    prev_row[j - 1] + cost,  # substitution
                )
            prev_row, curr_row = curr_row, prev_row

        return prev_row[m]

    @staticmethod
    def damerau_levenshtein_distance(s1: str, s2: str) -> int:
        """Compute Damerau-Levenshtein distance supporting insertions, deletions, substitutions, and transpositions."""
        n = len(s1)
        m = len(s2)

        if n == 0:
            return m
        if m == 0:
            return n

        # Full (n+1) x (m+1) DP matrix for adjacent transposition checks
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # deletion
                    dp[i][j - 1] + 1,  # insertion
                    dp[i - 1][j - 1] + cost,  # substitution
                )

                # Transposition check
                if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                    dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)

        return dp[n][m]

    @classmethod
    def domain_weighted_distance(
        cls,
        s1: str,
        s2: str,
        ins_cost: float = 1.0,
        del_cost: float = 1.0,
        sub_cost: float = 1.0,
        custom_substitutions: dict[tuple[str, str], float] | None = None,
    ) -> float:
        """Compute domain-weighted edit distance for fuzzy skill matching."""
        n = len(s1)
        m = len(s2)

        if n == 0:
            return m * ins_cost
        if m == 0:
            return n * del_cost

        sub_map = cls.DEFAULT_DOMAIN_SUBSTITUTIONS.copy()
        if custom_substitutions is not None:
            sub_map.update(custom_substitutions)

        dp = [[0.0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i * del_cost
        for j in range(m + 1):
            dp[0][j] = j * ins_cost

        for i in range(1, n + 1):
            c1 = s1[i - 1].lower()
            for j in range(1, m + 1):
                c2 = s2[j - 1].lower()
                if c1 == c2:
                    current_sub = 0.0
                else:
                    current_sub = sub_map.get((c1, c2), sub_cost)

                dp[i][j] = min(
                    dp[i - 1][j] + del_cost,
                    dp[i][j - 1] + ins_cost,
                    dp[i - 1][j - 1] + current_sub,
                )

                # Transposition with domain cost
                if (
                    i > 1
                    and j > 1
                    and s1[i - 1].lower() == s2[j - 2].lower()
                    and s1[i - 2].lower() == s2[j - 1].lower()
                ):
                    dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 0.8)

        return dp[n][m]

    @classmethod
    def normalized_similarity(cls, s1: str, s2: str, algorithm: str = "damerau") -> float:
        """Compute normalized similarity score in range [0.0, 1.0].

        1.0 means identical, 0.0 means completely disjoint.
        """
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0

        if algorithm == "levenshtein":
            dist = float(cls.levenshtein_distance(s1, s2))
        elif algorithm == "weighted":
            dist = cls.domain_weighted_distance(s1, s2)
        else:
            dist = float(cls.damerau_levenshtein_distance(s1, s2))

        score = 1.0 - (dist / float(max_len))
        return max(0.0, min(1.0, score))
