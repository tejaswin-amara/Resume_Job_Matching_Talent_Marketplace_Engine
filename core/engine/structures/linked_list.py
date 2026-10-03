"""CustomLinkedList: Doubly linked list with O(1) head/tail operations.

Zero-library constraint: built strictly using reference pointers and node objects.
"""

from typing import Iterator
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class ListNode(Generic[T]):
    """Doubly linked list node holding a value and bidirectional pointers."""

    __slots__ = ("next", "prev", "val")

    def __init__(
        self,
        val: T | None = None,
        prev: Optional["ListNode[T]"] = None,
        next_node: Optional["ListNode[T]"] = None,
    ) -> None:
        self.val: T | None = val
        self.prev: ListNode[T] | None = prev
        self.next: ListNode[T] | None = next_node

    def __repr__(self) -> str:
        return f"ListNode({self.val!r})"


class CustomLinkedList(Generic[T]):
    """Doubly linked list with sentinel nodes providing O(1) head and tail operations."""

    def __init__(self) -> None:
        self._head_sentinel: ListNode[T] = ListNode[T]()
        self._tail_sentinel: ListNode[T] = ListNode[T]()
        self._head_sentinel.next = self._tail_sentinel
        self._tail_sentinel.prev = self._head_sentinel
        self._size: int = 0

    def size(self) -> int:
        """Return the number of elements in the linked list."""
        return self._size

    def is_empty(self) -> bool:
        """Return True if the list contains no elements."""
        return self._size == 0

    def append(self, val: T) -> ListNode[T]:
        """Insert element at tail in O(1) time."""
        node = ListNode[T](val=val, prev=self._tail_sentinel.prev, next_node=self._tail_sentinel)
        assert self._tail_sentinel.prev is not None
        self._tail_sentinel.prev.next = node
        self._tail_sentinel.prev = node
        self._size += 1
        return node

    def append_left(self, val: T) -> ListNode[T]:
        """Insert element at head in O(1) time."""
        node = ListNode[T](val=val, prev=self._head_sentinel, next_node=self._head_sentinel.next)
        assert self._head_sentinel.next is not None
        self._head_sentinel.next.prev = node
        self._head_sentinel.next = node
        self._size += 1
        return node

    def pop(self) -> T:
        """Remove and return the element at the tail in O(1) time."""
        if self._size == 0:
            raise IndexError("pop from empty CustomLinkedList")
        last_node = self._tail_sentinel.prev
        assert last_node is not None
        return self.remove_node(last_node)

    def pop_left(self) -> T:
        """Remove and return the element at the head in O(1) time."""
        if self._size == 0:
            raise IndexError("pop_left from empty CustomLinkedList")
        first_node = self._head_sentinel.next
        assert first_node is not None
        return self.remove_node(first_node)

    def peek_front(self) -> T:
        """Return the value at the head without removing it."""
        if self._size == 0:
            raise IndexError("peek_front from empty CustomLinkedList")
        assert self._head_sentinel.next is not None
        return self._head_sentinel.next.val  # type: ignore

    def peek_back(self) -> T:
        """Return the value at the tail without removing it."""
        if self._size == 0:
            raise IndexError("peek_back from empty CustomLinkedList")
        assert self._tail_sentinel.prev is not None
        return self._tail_sentinel.prev.val  # type: ignore

    def remove_node(self, node: ListNode[T]) -> T:
        """Unlink an arbitrary node in O(1) time given its reference."""
        if node is self._head_sentinel or node is self._tail_sentinel:
            raise ValueError("Cannot remove sentinel nodes")
        if node.prev is None or node.next is None:
            raise ValueError("Node is not attached to this list")

        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1
        return node.val  # type: ignore

    def clear(self) -> None:
        """Clear all nodes from the list."""
        self._head_sentinel.next = self._tail_sentinel
        self._tail_sentinel.prev = self._head_sentinel
        self._size = 0

    def to_list(self) -> list[T]:
        """Convert elements to a standard primitive Python list."""
        result: list[T] = []
        curr = self._head_sentinel.next
        while curr is not None and curr is not self._tail_sentinel:
            result.append(curr.val)  # type: ignore
            curr = curr.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        curr = self._head_sentinel.next
        while curr is not None and curr is not self._tail_sentinel:
            yield curr.val  # type: ignore
            curr = curr.next

    def __repr__(self) -> str:
        return f"CustomLinkedList({self.to_list()!r})"
