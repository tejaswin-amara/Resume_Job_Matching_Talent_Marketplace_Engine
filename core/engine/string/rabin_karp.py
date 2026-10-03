"""RabinKarp: Dual-prime rolling hash for pattern search and plagiarism/duplicate detection.

Zero-library constraint: built strictly with primitive arrays and modular arithmetic.
"""

from typing import Any


class RabinKarp:
    """Dual-prime rolling hash string search and duplicate chunk detector."""

    # Two large coprime 31-bit / 32-bit primes
    MOD1: int = 1_000_000_007
    MOD2: int = 1_000_000_009
    BASE: int = 257

    @classmethod
    def hash_string(cls, s: str) -> tuple[int, int]:
        """Compute dual hash (h1, h2) for entire string."""
        h1 = 0
        h2 = 0
        for ch in s:
            val = ord(ch)
            h1 = (h1 * cls.BASE + val) % cls.MOD1
            h2 = (h2 * cls.BASE + val) % cls.MOD2
        return (h1, h2)

    @classmethod
    def find_all(cls, text: str, pattern: str) -> list[int]:
        """Find all 0-based start positions of pattern in text using dual-prime rolling hash."""
        n = len(text)
        m = len(pattern)

        if m == 0 or n == 0 or m > n:
            return []

        # Target hashes
        target_h1, target_h2 = cls.hash_string(pattern)

        # Precompute BASE^(m-1) mod MOD
        power1 = 1
        power2 = 1
        for _ in range(m - 1):
            power1 = (power1 * cls.BASE) % cls.MOD1
            power2 = (power2 * cls.BASE) % cls.MOD2

        # Initial window hash
        curr_h1 = 0
        curr_h2 = 0
        for i in range(m):
            val = ord(text[i])
            curr_h1 = (curr_h1 * cls.BASE + val) % cls.MOD1
            curr_h2 = (curr_h2 * cls.BASE + val) % cls.MOD2

        matches: list[int] = []

        for i in range(n - m + 1):
            if curr_h1 == target_h1 and curr_h2 == target_h2:
                # Full string verification to guard against spurious collision
                if text[i : i + m] == pattern:
                    matches.append(i)

            if i < n - m:
                # Slide window: subtract outgoing char, shift left, add incoming char
                out_val = ord(text[i])
                in_val = ord(text[i + m])

                curr_h1 = ((curr_h1 - out_val * power1) * cls.BASE + in_val) % cls.MOD1
                if curr_h1 < 0:
                    curr_h1 += cls.MOD1

                curr_h2 = ((curr_h2 - out_val * power2) * cls.BASE + in_val) % cls.MOD2
                if curr_h2 < 0:
                    curr_h2 += cls.MOD2

        return matches

    @classmethod
    def detect_duplicates(cls, doc_a: str, doc_b: str, k: int = 20) -> list[dict[str, Any]]:
        """Identify duplicate substrings of length >= k between doc_a and doc_b.

        Returns list of dicts with doc_a_start, doc_b_start, length, content.
        """
        len_a = len(doc_a)
        len_b = len(doc_b)

        if k <= 0 or len_a < k or len_b < k:
            return []

        # Map dual-hash -> list of start indices in doc_a
        # Using primitive dictionary or chaining
        hash_map_a: dict[tuple[int, int], list[int]] = {}

        power1 = 1
        power2 = 1
        for _ in range(k - 1):
            power1 = (power1 * cls.BASE) % cls.MOD1
            power2 = (power2 * cls.BASE) % cls.MOD2

        # Hash rolling k-grams of doc_a
        h1 = 0
        h2 = 0
        for i in range(k):
            val = ord(doc_a[i])
            h1 = (h1 * cls.BASE + val) % cls.MOD1
            h2 = (h2 * cls.BASE + val) % cls.MOD2

        for i in range(len_a - k + 1):
            key = (h1, h2)
            if key not in hash_map_a:
                hash_map_a[key] = []
            hash_map_a[key].append(i)

            if i < len_a - k:
                out_val = ord(doc_a[i])
                in_val = ord(doc_a[i + k])
                h1 = ((h1 - out_val * power1) * cls.BASE + in_val) % cls.MOD1
                if h1 < 0:
                    h1 += cls.MOD1
                h2 = ((h2 - out_val * power2) * cls.BASE + in_val) % cls.MOD2
                if h2 < 0:
                    h2 += cls.MOD2

        # Match with rolling k-grams of doc_b
        h1 = 0
        h2 = 0
        for i in range(k):
            val = ord(doc_b[i])
            h1 = (h1 * cls.BASE + val) % cls.MOD1
            h2 = (h2 * cls.BASE + val) % cls.MOD2

        matches: list[dict[str, Any]] = []

        for j in range(len_b - k + 1):
            key = (h1, h2)
            if key in hash_map_a:
                b_slice = doc_b[j : j + k]
                for a_start in hash_map_a[key]:
                    if doc_a[a_start : a_start + k] == b_slice:
                        matches.append(
                            {
                                "doc_a_start": a_start,
                                "doc_b_start": j,
                                "length": k,
                                "content": b_slice,
                            }
                        )

            if j < len_b - k:
                out_val = ord(doc_b[j])
                in_val = ord(doc_b[j + k])
                h1 = ((h1 - out_val * power1) * cls.BASE + in_val) % cls.MOD1
                if h1 < 0:
                    h1 += cls.MOD1
                h2 = ((h2 - out_val * power2) * cls.BASE + in_val) % cls.MOD2
                if h2 < 0:
                    h2 += cls.MOD2

        return matches

    @classmethod
    def similarity_score(cls, doc_a: str, doc_b: str, k: int = 20) -> float:
        """Compute Jaccard similarity of dual-hash k-gram fingerprint sets."""
        if len(doc_a) < k or len(doc_b) < k:
            return 1.0 if doc_a == doc_b else 0.0

        def get_kgram_hashes(doc: str) -> set[tuple[int, int]]:
            hashes: set[tuple[int, int]] = set()
            n = len(doc)
            power1 = 1
            power2 = 1
            for _ in range(k - 1):
                power1 = (power1 * cls.BASE) % cls.MOD1
                power2 = (power2 * cls.BASE) % cls.MOD2

            h1 = 0
            h2 = 0
            for i in range(k):
                val = ord(doc[i])
                h1 = (h1 * cls.BASE + val) % cls.MOD1
                h2 = (h2 * cls.BASE + val) % cls.MOD2

            for i in range(n - k + 1):
                hashes.add((h1, h2))
                if i < n - k:
                    out_val = ord(doc[i])
                    in_val = ord(doc[i + k])
                    h1 = ((h1 - out_val * power1) * cls.BASE + in_val) % cls.MOD1
                    if h1 < 0:
                        h1 += cls.MOD1
                    h2 = ((h2 - out_val * power2) * cls.BASE + in_val) % cls.MOD2
                    if h2 < 0:
                        h2 += cls.MOD2
            return hashes

        set_a = get_kgram_hashes(doc_a)
        set_b = get_kgram_hashes(doc_b)

        union_size = len(set_a | set_b)
        if union_size == 0:
            return 1.0

        intersection_size = len(set_a & set_b)
        return float(intersection_size) / float(union_size)
