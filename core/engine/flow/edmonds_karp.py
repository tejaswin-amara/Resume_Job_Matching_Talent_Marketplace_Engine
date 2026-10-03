"""EdmondsKarp: BFS-based Maximum Flow Algorithm in O(V * E^2) time.

Zero-library constraint: built strictly with primitive array BFS queues and residual edge pointers.
"""

from core.engine.structures.adjacency_graph import CustomAdjacencyGraph, FlowEdge


class EdmondsKarp:
    """Edmonds-Karp max flow algorithm using BFS augmenting paths."""

    EPSILON: float = 1e-9

    @classmethod
    def compute_max_flow(cls, graph: CustomAdjacencyGraph, source: int, sink: int) -> float:
        """Compute maximum s-t flow in graph in O(V * E^2) time."""
        if source == sink:
            return 0.0
        total_flow = 0.0
        num_nodes = max(graph.nodes() + [source, sink]) + 1

        while True:
            # BFS to find shortest augmenting path in terms of edge count
            parent_edge: list[FlowEdge | None] = [None] * num_nodes
            visited = [False] * num_nodes

            queue: list[int] = [source]
            visited[source] = True
            head = 0
            found_sink = False

            while head < len(queue):
                u = queue[head]
                head += 1

                if u == sink:
                    found_sink = True
                    break

                for edge in graph.get_edges(u):
                    v = edge.v
                    if not visited[v] and edge.residual_capacity > cls.EPSILON:
                        visited[v] = True
                        parent_edge[v] = edge
                        queue.append(v)

            if not found_sink:
                break

            # Find bottleneck capacity along the augmenting path
            bottleneck = float("inf")
            curr = sink
            while curr != source:
                edge = parent_edge[curr]
                assert edge is not None
                bottleneck = min(bottleneck, edge.residual_capacity)
                curr = edge.u

            if bottleneck <= cls.EPSILON:
                break

            # Augment flow along the path
            curr = sink
            while curr != source:
                edge = parent_edge[curr]
                assert edge is not None
                edge.augment(bottleneck)
                curr = edge.u

            total_flow += bottleneck

        return total_flow
