"""CustomHashMap: Chaining hash table with polynomial rolling hash and dynamic resizing.

Zero-library constraint: built strictly using primitive arrays and linked buckets.
Resize trigger: load factor >= 0.75.
"""

from collections.abc import Iterator
from typing import Any, Generic, Optional, TypeVar

from core.engine.structures.array_list import CustomArrayList

K = TypeVar("K")
V = TypeVar("V")


class HashNode(Generic[K, V]):
    """Singly linked entry in a hash bucket chain."""

    __slots__ = ("hash_code", "key", "next", "val")

    def __init__(
        self,
        key: K,
        val: V,
        hash_code: int,
        next_node: Optional["HashNode[K, V]"] = None,
    ) -> None:
        self.key: K = key
        self.val: V = val
        self.hash_code: int = hash_code
        self.next: HashNode[K, V] | None = next_node


class CustomHashMap(Generic[K, V]):
    """Separate-chaining hash table with polynomial rolling hash and dynamic resizing."""

    DEFAULT_INITIAL_CAPACITY: int = 16
    LOAD_FACTOR_THRESHOLD: float = 0.75
    POLYNOMIAL_BASE: int = 31
    LARGE_PRIME: int = 2147483647  # 2^31 - 1 (Mersenne prime)

    def __init__(self, initial_capacity: int | None = None) -> None:
        cap = (
            initial_capacity
            if (initial_capacity is not None and initial_capacity > 0)
            else self.DEFAULT_INITIAL_CAPACITY
        )
        # Ensure capacity is at least 4
        self._capacity: int = max(4, cap)
        self._size: int = 0
        self._buckets: list[HashNode[K, V] | None] = [None] * self._capacity

    def size(self) -> int:
        """Return the number of key-value pairs."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if the map contains no entries."""
        return self._size == 0

    def capacity(self) -> int:
        """Return the current number of buckets."""
        return self._capacity

    def load_factor(self) -> float:
        """Return current load factor (size / capacity)."""
        return self._size / self._capacity

    def _polynomial_rolling_hash(self, key: Any) -> int:
        """Compute polynomial rolling hash: sum(ord(c) * 31^i) mod (2^31 - 1)."""
        key_str = key if isinstance(key, str) else str(key)
        h = 0
        for char in key_str:
            h = (h * self.POLYNOMIAL_BASE + ord(char)) % self.LARGE_PRIME
        # Spread bits
        h = (h ^ (h >> 16)) & 0x7FFFFFFF
        return h

    def _bucket_index(self, hash_code: int, cap: int) -> int:
        """Map hash code to valid bucket index."""
        return hash_code % cap

    def _resize(self, new_capacity: int) -> None:
        """Double table size and rehash all entries."""
        new_buckets: list[HashNode[K, V] | None] = [None] * new_capacity
        for i in range(self._capacity):
            curr = self._buckets[i]
            while curr is not None:
                next_entry = curr.next
                idx = self._bucket_index(curr.hash_code, new_capacity)
                curr.next = new_buckets[idx]
                new_buckets[idx] = curr
                curr = next_entry

        self._buckets = new_buckets
        self._capacity = new_capacity

    def put(self, key: K, value: V) -> None:
        """Insert or update key-value pair in average O(1) time."""
        if (self._size + 1) / self._capacity >= self.LOAD_FACTOR_THRESHOLD:
            self._resize(self._capacity * 2)

        h = self._polynomial_rolling_hash(key)
        idx = self._bucket_index(h, self._capacity)

        curr = self._buckets[idx]
        while curr is not None:
            if curr.key == key:
                curr.val = value
                return
            curr = curr.next

        # Insert new node at bucket head
        new_node = HashNode[K, V](key=key, val=value, hash_code=h, next_node=self._buckets[idx])
        self._buckets[idx] = new_node
        self._size += 1

    def get(self, key: K, default: V | None = None) -> V | None:
        """Retrieve value for key or default in average O(1) time."""
        h = self._polynomial_rolling_hash(key)
        idx = self._bucket_index(h, self._capacity)

        curr = self._buckets[idx]
        while curr is not None:
            if curr.key == key:
                return curr.val
            curr = curr.next
        return default

    def contains(self, key: K) -> bool:
        """Return True if key exists in table."""
        h = self._polynomial_rolling_hash(key)
        idx = self._bucket_index(h, self._capacity)

        curr = self._buckets[idx]
        while curr is not None:
            if curr.key == key:
                return True
            curr = curr.next
        return False

    def remove(self, key: K) -> V:
        """Remove key from table and return its value; raise KeyError if not found."""
        h = self._polynomial_rolling_hash(key)
        idx = self._bucket_index(h, self._capacity)

        curr = self._buckets[idx]
        prev: HashNode[K, V] | None = None

        while curr is not None:
            if curr.key == key:
                if prev is None:
                    self._buckets[idx] = curr.next
                else:
                    prev.next = curr.next
                self._size -= 1
                return curr.val
            prev = curr
            curr = curr.next

        raise KeyError(f"Key not found: {key!r}")

    def keys(self) -> CustomArrayList[K]:
        """Return CustomArrayList containing all keys."""
        res: CustomArrayList[K] = CustomArrayList[K](self._size)
        for i in range(self._capacity):
            curr = self._buckets[i]
            while curr is not None:
                res.append(curr.key)
                curr = curr.next
        return res

    def values(self) -> CustomArrayList[V]:
        """Return CustomArrayList containing all values."""
        res: CustomArrayList[V] = CustomArrayList[V](self._size)
        for i in range(self._capacity):
            curr = self._buckets[i]
            while curr is not None:
                res.append(curr.val)
                curr = curr.next
        return res

    def items(self) -> CustomArrayList[tuple[K, V]]:
        """Return CustomArrayList of (key, value) tuples."""
        res: CustomArrayList[tuple[K, V]] = CustomArrayList[tuple[K, V]](self._size)
        for i in range(self._capacity):
            curr = self._buckets[i]
            while curr is not None:
                res.append((curr.key, curr.val))
                curr = curr.next
        return res

    def clear(self) -> None:
        """Clear all entries."""
        self._capacity = self.DEFAULT_INITIAL_CAPACITY
        self._size = 0
        self._buckets = [None] * self._capacity

    def __getitem__(self, key: K) -> V:
        val = self.get(key)
        if val is None and not self.contains(key):
            raise KeyError(f"Key not found: {key!r}")
        return val  # type: ignore

    def __setitem__(self, key: K, value: V) -> None:
        self.put(key, value)

    def __contains__(self, key: K) -> bool:
        return self.contains(key)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[K]:
        for i in range(self._capacity):
            curr = self._buckets[i]
            while curr is not None:
                yield curr.key
                curr = curr.next

    def __repr__(self) -> str:
        pairs = [f"{k!r}: {v!r}" for k, v in self.items()]
        return "CustomHashMap({" + ", ".join(pairs) + "})"
