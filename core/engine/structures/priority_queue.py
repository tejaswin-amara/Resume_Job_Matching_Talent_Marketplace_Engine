"""CustomPriorityQueue: Min/Max 4-ary heap with O(log4 n) insert and extract.

Zero-library constraint: built strictly on primitive arrays with 4-way tree branching.
"""

from typing import Generic, TypeVar

T = TypeVar("T")


class _HeapEntry(Generic[T]):
    """Internal entry in 4-ary heap storing priority, tie-breaker order, and item."""

    __slots__ = ("item", "order", "priority")

    def __init__(self, priority: float, order: int, item: T) -> None:
        self.priority: float = priority
        self.order: int = order
        self.item: T = item


class CustomPriorityQueue(Generic[T]):
    """4-ary (quaternary) heap supporting both Min-heap and Max-heap semantics."""

    ARITY: int = 4

    def __init__(self, is_min: bool = True, initial_capacity: int = 16) -> None:
        self._is_min: bool = is_min
        self._data: list[_HeapEntry[T] | None] = [None] * max(4, initial_capacity)
        self._size: int = 0
        self._counter: int = 0  # Tie-breaker for stable FIFO ordering on equal priorities

    def size(self) -> int:
        """Return number of elements in the heap."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if heap contains no elements."""
        return self._size == 0

    def _compares_better(self, a: _HeapEntry[T], b: _HeapEntry[T]) -> bool:
        """Determine whether entry `a` has strictly higher priority than `b`."""
        if self._is_min:
            if a.priority != b.priority:
                return a.priority < b.priority
            return a.order < b.order
        else:
            if a.priority != b.priority:
                return a.priority > b.priority
            return a.order < b.order

    def _resize(self, new_capacity: int) -> None:
        """Resize internal buffer to new_capacity."""
        new_data: list[_HeapEntry[T] | None] = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data

    def push(self, priority: float, item: T) -> None:
        """Insert element with priority into 4-ary heap in O(log4 n) time."""
        if self._size >= len(self._data):
            self._resize(len(self._data) * 2)

        entry = _HeapEntry[T](priority=float(priority), order=self._counter, item=item)
        self._counter += 1
        self._data[self._size] = entry
        self._sift_up(self._size)
        self._size += 1

    def _sift_up(self, index: int) -> None:
        """Restore heap property upwards in O(log4 n) time."""
        curr = index
        entry = self._data[curr]
        assert entry is not None

        while curr > 0:
            parent_idx = (curr - 1) // self.ARITY
            parent_entry = self._data[parent_idx]
            assert parent_entry is not None

            if self._compares_better(entry, parent_entry):
                self._data[curr] = parent_entry
                curr = parent_idx
            else:
                break

        self._data[curr] = entry

    def peek(self) -> tuple[float, T]:
        """Return (priority, item) of top element without removing it in O(1) time."""
        if self._size == 0:
            raise IndexError("peek from empty CustomPriorityQueue")
        top = self._data[0]
        assert top is not None
        return (top.priority, top.item)

    def pop(self) -> tuple[float, T]:
        """Remove and return top (priority, item) in O(log4 n) time."""
        if self._size == 0:
            raise IndexError("pop from empty CustomPriorityQueue")

        top = self._data[0]
        assert top is not None
        result = (top.priority, top.item)

        last_entry = self._data[self._size - 1]
        self._data[self._size - 1] = None
        self._size -= 1

        if self._size > 0:
            assert last_entry is not None
            self._data[0] = last_entry
            self._sift_down(0)

        # Shrink if oversized
        if self._size > 0 and self._size <= len(self._data) // 4 and len(self._data) > 16:
            self._resize(max(16, len(self._data) // 2))

        return result

    def _sift_down(self, index: int) -> None:
        """Restore heap property downwards in O(log4 n) time."""
        curr = index
        entry = self._data[curr]
        assert entry is not None

        while True:
            first_child = self.ARITY * curr + 1
            if first_child >= self._size:
                break

            best_child_idx = first_child
            best_child_entry = self._data[first_child]
            assert best_child_entry is not None

            last_child = min(self.ARITY * curr + self.ARITY, self._size - 1)
            for c in range(first_child + 1, last_child + 1):
                child_entry = self._data[c]
                assert child_entry is not None
                if self._compares_better(child_entry, best_child_entry):
                    best_child_entry = child_entry
                    best_child_idx = c

            if self._compares_better(best_child_entry, entry):
                self._data[curr] = best_child_entry
                curr = best_child_idx
            else:
                break

        self._data[curr] = entry

    def clear(self) -> None:
        """Clear all entries."""
        self._data = [None] * 16
        self._size = 0
        self._counter = 0

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        mode = "min" if self._is_min else "max"
        return f"CustomPriorityQueue(mode={mode!r}, size={self._size})"
