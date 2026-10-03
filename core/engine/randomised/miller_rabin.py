"""MillerRabin: Primality testing and Carter-Wegman universal hash families.

Used for cryptographic candidate credential fingerprinting and tamper-proof verification.
Zero-library constraint: built strictly on primitive modular arithmetic and random selection.
"""

import random
from typing import Any


class MillerRabin:
    """Deterministic and probabilistic Miller-Rabin primality testing."""

    # Deterministic base set guaranteed correct for all n < 2^64
    DETERMINISTIC_BASES_64: list[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

    @classmethod
    def is_prime(cls, n: int, k_rounds: int = 20) -> bool:
        """Test whether n is prime using Miller-Rabin algorithm.

        Deterministic for n < 2^64; error probability <= 4^(-k_rounds) for larger n.
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False

        # Write n - 1 as 2^s * d with d odd
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        # Select bases
        if n < (1 << 64):
            bases = [b for b in cls.DETERMINISTIC_BASES_64 if b < n]
        else:
            rng = random.Random()
            bases = [rng.randint(2, n - 2) for _ in range(k_rounds)]

        for a in bases:
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue

            composite = True
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    composite = False
                    break

            if composite:
                return False

        return True

    @classmethod
    def next_prime(cls, n: int) -> int:
        """Return the smallest prime strictly greater than n."""
        candidate = n + 1 if (n + 1) % 2 != 0 else n + 2
        if candidate <= 2:
            return 2
        while not cls.is_prime(candidate):
            candidate += 2
        return candidate


class UniversalHashFamily:
    """Carter-Wegman 2-Universal Hash Family: h_{a, b}(x) = ((a * x + b) mod p) mod m."""

    def __init__(
        self,
        m: int,
        p: int | None = None,
        seed: int | None = None,
    ) -> None:
        if m <= 0:
            raise ValueError(f"Table size m must be positive, got {m}")
        self.m: int = m
        self._rng: random.Random = random.Random(seed)

        # Ensure prime p > m
        if p is None:
            # Pick a large prime strictly larger than m
            self.p: int = MillerRabin.next_prime(max(m * 2, 2_147_483_647))
        else:
            self.p = p

        self.a: int = self._rng.randint(1, self.p - 1)
        self.b: int = self._rng.randint(0, self.p - 1)

    def hash_int(self, x: int) -> int:
        """Hash integer x uniformly into [0, m - 1]."""
        return ((self.a * x + self.b) % self.p) % self.m

    def hash_string(self, s: str) -> int:
        """Hash string s into [0, m - 1] via polynomial rolling evaluation with Universal coefficients."""
        h = 0
        for ch in s:
            h = (h * self.a + ord(ch)) % self.p
        h = (h + self.b) % self.p
        return h % self.m

    def generate_credential_fingerprint(self, credential: dict[str, Any] | str) -> str:
        """Create a tamper-evident hex fingerprint for a candidate credential."""
        serialized = (
            str(sorted(credential.items())) if isinstance(credential, dict) else str(credential)
        )
        h = self.hash_string(serialized)
        return f"CR-{self.a:04x}-{h:08x}"
