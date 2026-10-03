"""Unit tests for Custom Data Structures (DSA Module M1).

Verifies CustomArrayList, CustomLinkedList, CustomHashMap, CustomPriorityQueue, and CustomAdjacencyGraph.
Zero-library verification: pure algorithmic correctness, edge cases, and bounds checking.
"""

import pytest

from core.engine.structures.adjacency_graph import CustomAdjacencyGraph
from core.engine.structures.array_list import CustomArrayList
from core.engine.structures.hash_map import CustomHashMap
from core.engine.structures.linked_list import CustomLinkedList
from core.engine.structures.priority_queue import CustomPriorityQueue

# ==============================================================================
# 1. CustomArrayList Tests
# ==============================================================================


def test_array_list_basic_operations():
    arr = CustomArrayList[int](initial_capacity=4)
    assert arr.size() == 0
    assert arr.is_empty()
    assert len(arr) == 0

    # Append triggers geometric growth
    for i in range(10):
        arr.append(i * 10)

    assert arr.size() == 10
    assert not arr.is_empty()
    assert arr.capacity() >= 16

    # Indexing
    assert arr.get(0) == 0
    assert arr.get(9) == 90
    assert arr.get(-1) == 90
    assert arr.get(-10) == 0

    # Setting
    arr.set(0, 999)
    assert arr[0] == 999

    # Out of bounds
    with pytest.raises(IndexError):
        arr.get(10)
    with pytest.raises(IndexError):
        arr.get(-11)


def test_array_list_insert_and_pop():
    arr = CustomArrayList[str]()
    arr.append("b")
    arr.append("d")
    arr.insert(0, "a")
    arr.insert(2, "c")
    arr.insert(4, "e")

    assert arr.to_list() == ["a", "b", "c", "d", "e"]

    # Pop middle
    removed = arr.pop(2)
    assert removed == "c"
    assert arr.to_list() == ["a", "b", "d", "e"]

    # Pop end
    removed_end = arr.pop()
    assert removed_end == "e"
    assert arr.to_list() == ["a", "b", "d"]

    # Pop front
    removed_front = arr.pop(0)
    assert removed_front == "a"
    assert arr.to_list() == ["b", "d"]


def test_array_list_iteration_and_clear():
    arr = CustomArrayList[int]()
    arr.extend([1, 2, 3, 4, 5])
    assert list(arr) == [1, 2, 3, 4, 5]

    arr2 = CustomArrayList[int]()
    arr2.extend([1, 2, 3, 4, 5])
    assert arr == arr2

    arr.clear()
    assert arr.size() == 0
    assert arr.is_empty()
    with pytest.raises(IndexError):
        arr.pop()


# ==============================================================================
# 2. CustomLinkedList Tests
# ==============================================================================


def test_linked_list_basic_operations():
    ll = CustomLinkedList[int]()
    assert ll.is_empty()
    assert len(ll) == 0

    # Append and append_left
    ll.append(20)
    ll.append(30)
    ll.append_left(10)
    ll.append_left(0)

    assert ll.to_list() == [0, 10, 20, 30]
    assert ll.size() == 4
    assert ll.peek_front() == 0
    assert ll.peek_back() == 30

    # Pop and pop_left
    assert ll.pop_left() == 0
    assert ll.pop() == 30
    assert ll.to_list() == [10, 20]
    assert ll.size() == 2


def test_linked_list_remove_arbitrary_node():
    ll = CustomLinkedList[str]()
    n1 = ll.append("first")
    n2 = ll.append("second")
    n3 = ll.append("third")

    assert ll.remove_node(n2) == "second"
    assert ll.to_list() == ["first", "third"]
    assert ll.size() == 2

    # Attempting to remove already unlinked node
    with pytest.raises(ValueError):
        ll.remove_node(n2)


def test_linked_list_empty_errors():
    ll = CustomLinkedList[int]()
    with pytest.raises(IndexError):
        ll.pop()
    with pytest.raises(IndexError):
        ll.pop_left()
    with pytest.raises(IndexError):
        ll.peek_front()
    with pytest.raises(IndexError):
        ll.peek_back()


# ==============================================================================
# 3. CustomHashMap Tests
# ==============================================================================


def test_hash_map_crud_and_resize():
    hmap = CustomHashMap[str, int](initial_capacity=8)
    assert hmap.size() == 0
    assert hmap.is_empty()

    # Insert items
    for i in range(20):
        hmap.put(f"key_{i}", i * 100)

    assert hmap.size() == 20
    assert hmap.capacity() >= 32  # Verified dynamic resizing at >= 0.75
    assert hmap.load_factor() < 0.75

    # Retrieve items
    for i in range(20):
        assert hmap.get(f"key_{i}") == i * 100
        assert hmap.contains(f"key_{i}")
        assert f"key_{i}" in hmap

    # Update value
    hmap.put("key_5", 55555)
    assert hmap.get("key_5") == 55555
    assert hmap.size() == 20  # Size unchanged on update

    # Missing key
    assert hmap.get("non_existent") is None
    assert hmap.get("non_existent", -1) == -1
    assert "non_existent" not in hmap

    with pytest.raises(KeyError):
        _ = hmap["non_existent"]


def test_hash_map_remove_and_keys():
    hmap = CustomHashMap[str, str]()
    hmap["python"] = "expert"
    hmap["fastapi"] = "advanced"
    hmap["docker"] = "intermediate"

    assert hmap.size() == 3
    assert hmap.remove("fastapi") == "advanced"
    assert hmap.size() == 2
    assert "fastapi" not in hmap

    with pytest.raises(KeyError):
        hmap.remove("fastapi")

    # Keys returns CustomArrayList
    keys_arr = hmap.keys()
    assert isinstance(keys_arr, CustomArrayList)
    assert set(keys_arr.to_list()) == {"python", "docker"}


# ==============================================================================
# 4. CustomPriorityQueue Tests (4-ary Min and Max Heap)
# ==============================================================================


def test_priority_queue_min_heap():
    pq = CustomPriorityQueue[str](is_min=True)
    assert pq.is_empty()

    items = [(5.0, "e"), (1.0, "a"), (3.0, "c"), (2.0, "b"), (4.0, "d"), (0.5, "zero")]
    for p, item in items:
        pq.push(p, item)

    assert pq.size() == 6
    assert pq.peek() == (0.5, "zero")

    extracted = []
    while not pq.is_empty():
        extracted.append(pq.pop())

    # Strictly sorted in ascending order of priority
    priorities = [p for p, _ in extracted]
    assert priorities == sorted(priorities)
    assert [item for _, item in extracted] == ["zero", "a", "b", "c", "d", "e"]


def test_priority_queue_max_heap():
    pq = CustomPriorityQueue[str](is_min=False)
    for p, item in [(10.0, "low"), (90.0, "high"), (50.0, "mid"), (90.0, "high2")]:
        pq.push(p, item)

    top_p, top_item = pq.pop()
    assert top_p == 90.0
    assert top_item == "high"  # Stable FIFO tie-breaking on identical priorities

    second_p, second_item = pq.pop()
    assert second_p == 90.0
    assert second_item == "high2"

    assert pq.pop() == (50.0, "mid")
    assert pq.pop() == (10.0, "low")
    assert pq.is_empty()

    with pytest.raises(IndexError):
        pq.pop()


# ==============================================================================
# 5. CustomAdjacencyGraph Tests
# ==============================================================================


def test_adjacency_graph_edges_and_residuals():
    graph = CustomAdjacencyGraph()
    graph.add_node(1)
    graph.add_node(2)
    e = graph.add_edge(1, 2, capacity=10.0, cost=2.5)

    assert e.u == 1
    assert e.v == 2
    assert e.capacity == 10.0
    assert e.flow == 0.0
    assert e.cost == 2.5
    assert e.residual_capacity == 10.0

    # Anti-parallel residual edge
    rev = e.residual
    assert rev is not None
    assert rev.u == 2
    assert rev.v == 1
    assert rev.capacity == 0.0
    assert rev.flow == 0.0
    assert rev.cost == -2.5
    assert rev.residual_capacity == 0.0

    # Augment 4 units
    e.augment(4.0)
    assert e.flow == 4.0
    assert e.residual_capacity == 6.0
    assert rev.flow == -4.0
    assert rev.residual_capacity == 4.0

    assert graph.get_residual_capacity(1, 2) == 6.0
    assert graph.get_residual_capacity(2, 1) == 4.0

    # Reset
    graph.reset_flow()
    assert e.flow == 0.0
    assert e.residual_capacity == 10.0
