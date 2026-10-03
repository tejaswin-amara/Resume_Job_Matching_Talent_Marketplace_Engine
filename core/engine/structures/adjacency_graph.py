"""CustomAdjacencyGraph: Flow network graph with forward and residual edge pointers.

Zero-library constraint: built strictly on primitive lists and linked Edge object references.
"""

from typing import Iterator
from typing import Optional


class FlowEdge:
    """Directed edge in flow network with pointer to its anti-parallel residual counterpart."""

    __slots__ = ("capacity", "cost", "flow", "residual", "u", "v")

    def __init__(
        self,
        u: int,
        v: int,
        capacity: float,
        cost: float = 0.0,
        residual: Optional["FlowEdge"] = None,
    ) -> None:
        self.u: int = u
        self.v: int = v
        self.capacity: float = float(capacity)
        self.flow: float = 0.0
        self.cost: float = float(cost)
        self.residual: FlowEdge | None = residual

    @property
    def residual_capacity(self) -> float:
        """Return remaining available residual capacity."""
        return self.capacity - self.flow

    def augment(self, push_flow: float) -> None:
        """Augment flow along forward edge and decrease flow on residual edge."""
        self.flow += push_flow
        assert self.residual is not None
        self.residual.flow -= push_flow

    def __repr__(self) -> str:
        return f"FlowEdge({self.u} -> {self.v}, cap={self.capacity}, flow={self.flow}, cost={self.cost})"


class CustomAdjacencyGraph:
    """Adjacency list graph with integrated forward and residual edge pointers."""

    def __init__(self, initial_node_count: int = 16) -> None:
        self._adj: list[list[FlowEdge]] = [[] for _ in range(max(16, initial_node_count))]
        self._nodes: set[int] = set()

    def _ensure_node(self, node_id: int) -> None:
        """Ensure adjacency list has capacity for node_id."""
        if node_id >= len(self._adj):
            new_size = max(node_id + 1, len(self._adj) * 2)
            while len(self._adj) < new_size:
                self._adj.append([])
        self._nodes.add(node_id)

    def add_node(self, node_id: int) -> None:
        """Explicitly register a node in the graph."""
        self._ensure_node(node_id)

    def add_edge(self, u: int, v: int, capacity: float, cost: float = 0.0) -> FlowEdge:
        """Add forward edge u->v with capacity and reverse residual edge v->u with 0 capacity."""
        self._ensure_node(u)
        self._ensure_node(v)

        forward = FlowEdge(u, v, capacity, cost)
        backward = FlowEdge(v, u, 0.0, -cost, residual=forward)
        forward.residual = backward

        self._adj[u].append(forward)
        self._adj[v].append(backward)
        return forward

    def get_edges(self, u: int) -> list[FlowEdge]:
        """Return list of outgoing edges (including residual edges) from node u."""
        if u < len(self._adj):
            return self._adj[u]
        return []

    def get_residual_capacity(self, u: int, v: int) -> float:
        """Return remaining residual capacity on edge u->v.

        If multiple parallel edges exist, sums residual capacity.
        """
        if u >= len(self._adj):
            return 0.0
        total_res = 0.0
        found = False
        for edge in self._adj[u]:
            if edge.v == v:
                total_res += edge.residual_capacity
                found = True
        return total_res if found else 0.0

    def nodes(self) -> list[int]:
        """Return sorted list of all active node IDs."""
        return sorted(list(self._nodes))

    def node_count(self) -> int:
        """Return total count of distinct registered nodes."""
        return len(self._nodes)

    def reset_flow(self) -> None:
        """Reset flow on all edges to 0."""
        for u in self._nodes:
            for edge in self._adj[u]:
                edge.flow = 0.0

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[int]:
        return iter(self.nodes())
