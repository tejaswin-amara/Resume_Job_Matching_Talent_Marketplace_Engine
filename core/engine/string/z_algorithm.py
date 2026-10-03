"""ZAlgorithm: Exact pattern matching and prefix-suffix analysis in linear O(N + M) time.

Zero-library constraint: built strictly with primitive arrays and pointer loops.
"""


class ZAlgorithm:
    """Z-Algorithm for linear-time string search and longest common prefix computations."""

    @staticmethod
    def compute_z_array(s: str) -> list[int]:
        """Compute Z-array for string s in O(|s|) time.

        Z[i] is the length of the longest substring starting from s[i]
        which is also a prefix of s. Z[0] is set to len(s).
        """
        n = len(s)
        if n == 0:
            return []

        z = [0] * n
        z[0] = n

        # [l, r] maintains the interval with maximum r such that s[l..r] is a prefix of s
        l = 0
        r = 0

        for i in range(1, n):
            if i <= r:
                # Inside current Z-box
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    # Need to expand past r
                    l = i
                    while r < n and s[r] == s[r - l]:
                        r += 1
                    z[i] = r - l
                    r -= 1
            else:
                # Outside current Z-box
                l = i
                r = i
                while r < n and s[r] == s[r - l]:
                    r += 1
                z[i] = r - l
                r -= 1

        return z

    @classmethod
    def search(cls, text: str, pattern: str, delimiter: str = "\x00") -> list[int]:
        """Search for all occurrences of pattern in text using Z-array in O(N + M).

        Returns 0-based start indices in text.
        """
        n = len(text)
        m = len(pattern)

        if m == 0 or n == 0 or m > n:
            return []

        # Construct combined string: pattern + delimiter + text
        concat = pattern + delimiter + text
        z = cls.compute_z_array(concat)

        matches: list[int] = []
        for i in range(m + 1, len(concat)):
            if z[i] >= m:
                # Start index in text is i - (m + 1)
                matches.append(i - (m + 1))

        return matches
