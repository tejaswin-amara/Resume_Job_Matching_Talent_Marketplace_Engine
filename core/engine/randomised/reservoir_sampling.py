"""ReservoirSampler: Algorithm R for unbiased streaming applicant sampling.

Maintains a uniform random sample of size k from an unbounded stream of arbitrary length N.
Every item in the stream has an exact equal probability k / N of being retained.
Zero-library constraint: built strictly on primitive arrays and random index selection.
"""

import random
from collections.abc import Iterator, Sequence
from typing import Generic, TypeVar

T = TypeVar("T")


class ReservoirSampler(Generic[T]):
    """Streaming uniform reservoir sampler implementing Algorithm R."""

    def __init__(self, k: int, seed: int | None = None) -> None:
        if k <= 0:
            raise ValueError(f"Reservoir capacity k must be positive, got {k}")
        self.k: int = k
        self._reservoir: list[T] = []
        self._count: int = 0
        self._rng: random.Random = random.Random(seed)

    @property
    def capacity(self) -> int:
        """Return the reservoir size k."""
        return self.k

    @property
    def total_stream_items_seen(self) -> int:
        """Return total items observed in the stream so far."""
        return self._count

    def add(self, item: T) -> bool:
        """Observe an incoming item from the stream.

        Returns True if item was placed in the reservoir, False otherwise.
        """
        self._count += 1
        if len(self._reservoir) < self.k:
            self._reservoir.append(item)
            return True

        # For item count > k, select with probability k / count
        j = self._rng.randint(0, self._count - 1)
        if j < self.k:
            self._reservoir[j] = item
            return True

        return False

    def get_sample(self) -> list[T]:
        """Return current contents of the reservoir."""
        return list(self._reservoir)

    def reset(self) -> None:
        """Clear reservoir and reset stream count."""
        self._reservoir = []
        self._count = 0

    @classmethod
    def sample_stream(
        cls,
        stream: Iterator[T] | Sequence[T],
        k: int,
        seed: int | None = None,
    ) -> list[T]:
        """Convenience method to sample k elements from a given stream or collection."""
        sampler = cls(k=k, seed=seed)
        for item in stream:
            sampler.add(item)
        return sampler.get_sample()
