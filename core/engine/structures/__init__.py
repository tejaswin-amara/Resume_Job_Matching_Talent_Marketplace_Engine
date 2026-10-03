"""Custom zero-library data structures.

All data structures are implemented from scratch using primitive arrays and pointer references.
"""

from core.engine.structures.adjacency_graph import CustomAdjacencyGraph, FlowEdge
from core.engine.structures.array_list import CustomArrayList
from core.engine.structures.hash_map import CustomHashMap
from core.engine.structures.linked_list import CustomLinkedList, ListNode
from core.engine.structures.priority_queue import CustomPriorityQueue

__all__ = [
    "CustomAdjacencyGraph",
    "CustomArrayList",
    "CustomHashMap",
    "CustomLinkedList",
    "CustomPriorityQueue",
    "FlowEdge",
    "ListNode",
]
