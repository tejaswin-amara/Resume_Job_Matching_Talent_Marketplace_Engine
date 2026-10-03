"""SuffixArray and KasaiLCP: O(N log^2 N) suffix array construction and O(N) LCP.

Zero-library constraint: built with prefix doubling and Kasai's theorem.
"""


class SuffixArray:
    """Suffix array construction via O(N log^2 N) prefix doubling."""

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.n: int = len(text)
        self.sa: list[int] = self._build_suffix_array(text)

    def _build_suffix_array(self, s: str) -> list[int]:
        """Construct suffix array using prefix doubling algorithm."""
        n = len(s)
        if n == 0:
            return []
        if n == 1:
            return [0]

        # Initial rank based on character ASCII values
        rank = [ord(c) for c in s]
        sa = list(range(n))

        k = 1
        while k < n:
            # Pair: (rank[i], rank[i + k] if i + k < n else -1)
            # Custom rank comparator
            sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))

            new_rank = [0] * n
            new_rank[sa[0]] = 0
            distinct = True

            for idx in range(1, n):
                prev_i = sa[idx - 1]
                curr_i = sa[idx]
                prev_pair = (rank[prev_i], rank[prev_i + k] if prev_i + k < n else -1)
                curr_pair = (rank[curr_i], rank[curr_i + k] if curr_i + k < n else -1)

                if curr_pair == prev_pair:
                    new_rank[curr_i] = new_rank[prev_i]
                    distinct = False
                else:
                    new_rank[curr_i] = new_rank[prev_i] + 1

            rank = new_rank
            if distinct or rank[sa[-1]] == n - 1:
                break
            k *= 2

        return sa

    def get_suffix_array(self) -> list[int]:
        """Return the computed suffix array."""
        return self.sa


class KasaiLCP:
    """Kasai's algorithm to compute Longest Common Prefix (LCP) array in linear O(N) time."""

    @staticmethod
    def compute_lcp(text: str, sa: list[int]) -> list[int]:
        """Compute LCP array where lcp[i] = length of LCP(suffix[sa[i]], suffix[sa[i-1]]).

        lcp[0] is set to 0. Runs in strictly O(N) time.
        """
        n = len(text)
        if n == 0:
            return []
        if n == 1:
            return [0]

        # rank_pos maps suffix start index to its position in the suffix array
        rank_pos = [0] * n
        for idx in range(n):
            rank_pos[sa[idx]] = idx

        lcp = [0] * n
        h = 0

        for i in range(n):
            curr_pos = rank_pos[i]
            if curr_pos > 0:
                prev_suffix_idx = sa[curr_pos - 1]
                while (
                    i + h < n
                    and prev_suffix_idx + h < n
                    and text[i + h] == text[prev_suffix_idx + h]
                ):
                    h += 1
                lcp[curr_pos] = h
                if h > 0:
                    h -= 1

        return lcp

    @classmethod
    def longest_repeated_substring(cls, text: str) -> str:
        """Find the longest substring that appears at least twice in text."""
        if len(text) <= 1:
            return ""

        sa = SuffixArray(text).get_suffix_array()
        lcp = cls.compute_lcp(text, sa)

        max_len = 0
        best_pos = 0

        for i in range(1, len(lcp)):
            if lcp[i] > max_len:
                max_len = lcp[i]
                best_pos = sa[i]

        return text[best_pos : best_pos + max_len] if max_len > 0 else ""

    @classmethod
    def longest_common_substring(cls, s1: str, s2: str, separator: str = "#") -> str:
        """Find the longest common substring between two strings using concatenated suffix array."""
        if not s1 or not s2:
            return ""

        combined = s1 + separator + s2
        len1 = len(s1)
        sa = SuffixArray(combined).get_suffix_array()
        lcp = KasaiLCP.compute_lcp(combined, sa)

        max_len = 0
        best_start = 0

        for i in range(1, len(sa)):
            idx1 = sa[i - 1]
            idx2 = sa[i]

            # One suffix must belong to s1 and the other to s2
            belongs_s1_a = idx1 < len1
            belongs_s1_b = idx2 < len1

            if belongs_s1_a != belongs_s1_b:
                common_len = lcp[i]
                if common_len > max_len:
                    # Make sure it doesn't include the separator
                    # Start index from whichever belongs to s1
                    s1_start = idx1 if belongs_s1_a else idx2
                    actual_len = min(common_len, len1 - s1_start)
                    if actual_len > max_len:
                        max_len = actual_len
                        best_start = s1_start

        return s1[best_start : best_start + max_len] if max_len > 0 else ""
