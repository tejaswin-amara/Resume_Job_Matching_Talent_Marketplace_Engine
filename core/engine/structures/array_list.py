"""CustomArrayList: Resizable array with geometric amortized O(1) append.

Zero-library constraint: built strictly using primitive arrays and pointer math.
"""

from collections.abc import Iterator
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class CustomArrayList(Generic[T]):
    """Dynamic array backed by a primitive fixed-size buffer.

    Amortized O(1) append via geometric capacity doubling.
    """

    DEFAULT_INITIAL_CAPACITY: int = 8
    GROWTH_FACTOR: int = 2

    def __init__(self, initial_capacity: int | None = None) -> None:
        cap = (
            initial_capacity
            if (initial_capacity is not None and initial_capacity > 0)
            else self.DEFAULT_INITIAL_CAPACITY
        )
        self._capacity: int = cap
        self._size: int = 0
        self._data: list[T | None] = [None] * self._capacity

    def size(self) -> int:
        """Return the current number of elements."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if the array contains no elements."""
        return self._size == 0

    def capacity(self) -> int:
        """Return the internal allocated buffer capacity."""
        return self._capacity

    def _resize(self, new_capacity: int) -> None:
        """Resize the internal buffer to new_capacity."""
        new_data: list[T | None] = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def append(self, item: T) -> None:
        """Append an item to the end in amortized O(1) time."""
        if self._size >= self._capacity:
            self._resize(self._capacity * self.GROWTH_FACTOR)
        self._data[self._size] = item
        self._size += 1

    def _validate_index(self, index: int) -> int:
        """Validate and normalize index, supporting negative indexing."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError(
                f"Index {index} out of bounds for CustomArrayList of size {self._size}"
            )
        return index

    def get(self, index: int) -> T:
        """Get element at 0-based index in O(1) time."""
        norm_idx = self._validate_index(index)
        item = self._data[norm_idx]
        return item  # type: ignore

    def set(self, index: int, item: T) -> None:
        """Set element at 0-based index in O(1) time."""
        norm_idx = self._validate_index(index)
        self._data[norm_idx] = item

    def insert(self, index: int, item: T) -> None:
        """Insert item at index, shifting subsequent elements right."""
        if index < 0:
            index += self._size
        index = max(index, 0)
        index = min(index, self._size)

        if self._size >= self._capacity:
            self._resize(self._capacity * self.GROWTH_FACTOR)

        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]

        self._data[index] = item
        self._size += 1

    def pop(self, index: int = -1) -> T:
        """Remove and return element at index (defaults to last element)."""
        if self._size == 0:
            raise IndexError("pop from empty CustomArrayList")
        norm_idx = self._validate_index(index)
        item = self._data[norm_idx]

        for i in range(norm_idx, self._size - 1):
            self._data[i] = self._data[i + 1]

        self._data[self._size - 1] = None
        self._size -= 1

        # Shrink capacity if load factor drops below 0.25 to prevent memory bloat
        if (
            self._size > 0
            and self._size <= self._capacity // 4
            and self._capacity > self.DEFAULT_INITIAL_CAPACITY
        ):
            new_cap = max(self.DEFAULT_INITIAL_CAPACITY, self._capacity // 2)
            self._resize(new_cap)

        return item  # type: ignore

    def clear(self) -> None:
        """Clear all elements and reset to default capacity."""
        self._capacity = self.DEFAULT_INITIAL_CAPACITY
        self._size = 0
        self._data = [None] * self._capacity

    def extend(self, iterable: Any) -> None:
        """Append elements from an iterable."""
        for item in iterable:
            self.append(item)

    def to_list(self) -> list[T]:
        """Convert elements to a standard primitive Python list."""
        result: list[T] = []
        for i in range(self._size):
            result.append(self._data[i])  # type: ignore
        return result

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __setitem__(self, index: int, item: T) -> None:
        self.set(index, item)

    def __iter__(self) -> Iterator[T]:
        for i in range(self._size):
            yield self._data[i]  # type: ignore

    def __repr__(self) -> str:
        items_str = ", ".join(repr(self._data[i]) for i in range(self._size))
        return f"CustomArrayList([{items_str}])"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CustomArrayList):
            return False
        if self._size != other._size:
            return False
        for i in range(self._size):
            if self._data[i] != other._data[i]:
                return False
        return True
