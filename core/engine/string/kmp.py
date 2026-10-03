"""KMPMatcher: Knuth-Morris-Pratt string matching algorithm in O(N + M).

Zero-library constraint: built strictly with primitive arrays and pointer loops.
"""


class KMPMatcher:
    """Knuth-Morris-Pratt pattern matching engine with prefix table computation."""

    @staticmethod
    def compute_prefix_function(pattern: str) -> list[int]:
        """Compute the KMP prefix failure table (pi array) in O(M) time.

        pi[i] is the length of the longest proper prefix of pattern[0..i]
        that is also a suffix of pattern[0..i].
        """
        m = len(pattern)
        if m == 0:
            return []

        pi = [0] * m
        j = 0
        for i in range(1, m):
            while j > 0 and pattern[i] != pattern[j]:
                j = pi[j - 1]
            if pattern[i] == pattern[j]:
                j += 1
            pi[i] = j
        return pi

    @classmethod
    def find_all(cls, text: str, pattern: str) -> list[int]:
        """Find all 0-based start indices of pattern in text in O(N + M) time."""
        n = len(text)
        m = len(pattern)

        if m == 0 or n == 0 or m > n:
            return []

        pi = cls.compute_prefix_function(pattern)
        matches: list[int] = []

        j = 0  # Number of characters matched in pattern
        for i in range(n):
            while j > 0 and text[i] != pattern[j]:
                j = pi[j - 1]
            if text[i] == pattern[j]:
                j += 1
            if j == m:
                matches.append(i - m + 1)
                j = pi[j - 1]

        return matches

    @classmethod
    def find_first(cls, text: str, pattern: str) -> int:
        """Find the first 0-based start index of pattern in text, or -1 if not found."""
        n = len(text)
        m = len(pattern)

        if m == 0 or n == 0 or m > n:
            return -1

        pi = cls.compute_prefix_function(pattern)
        j = 0
        for i in range(n):
            while j > 0 and text[i] != pattern[j]:
                j = pi[j - 1]
            if text[i] == pattern[j]:
                j += 1
            if j == m:
                return i - m + 1

        return -1

    @classmethod
    def count_occurrences(cls, text: str, pattern: str) -> int:
        """Return the count of non-overlapping or overlapping occurrences of pattern in text."""
        return len(cls.find_all(text, pattern))
