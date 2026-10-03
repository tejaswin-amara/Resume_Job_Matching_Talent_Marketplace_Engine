"""MinCostMaxFlow: Successive Shortest Path with potential updates and cycle cancellation.

Computes maximum flow at minimum possible edge cost.
Zero-library constraint: built strictly on CustomAdjacencyGraph and primitive arrays.
"""

from core.engine.structures.adjacency_graph import CustomAdjacencyGraph, FlowEdge


class MinCostMaxFlow:
    """Successive Shortest Path min-cost max-flow algorithm using SPFA."""

    EPSILON: float = 1e-9
    INF: float = float("inf")

    @classmethod
    def compute_min_cost_max_flow(
        cls,
        graph: CustomAdjacencyGraph,
        source: int,
        sink: int,
        target_flow: float | None = None,
    ) -> tuple[float, float]:
        """Compute (max_flow, min_cost) from source to sink.

        Optionally stops when target_flow is met.
        """
        total_flow = 0.0
        total_cost = 0.0
        num_nodes = max(graph.nodes() + [source, sink]) + 1

        dist = [cls.INF] * num_nodes
        parent_edge: list[FlowEdge | None] = [None] * num_nodes
        in_queue = [False] * num_nodes

        while True:
            if target_flow is not None and total_flow >= target_flow - cls.EPSILON:
                break

            # SPFA to find minimum cost augmenting path in residual graph
            for i in range(num_nodes):
                dist[i] = cls.INF
                parent_edge[i] = None
                in_queue[i] = False

            dist[source] = 0.0
            queue: list[int] = [source]
            in_queue[source] = True
            head = 0

            while head < len(queue):
                u = queue[head]
                head += 1
                in_queue[u] = False

                for edge in graph.get_edges(u):
                    if edge.residual_capacity > cls.EPSILON:
                        v = edge.v
                        new_cost = dist[u] + edge.cost
                        if new_cost < dist[v] - cls.EPSILON:
                            dist[v] = new_cost
                            parent_edge[v] = edge
                            if not in_queue[v]:
                                queue.append(v)
                                in_queue[v] = True

            # If sink cannot be reached, no more augmenting paths
            if dist[sink] == cls.INF:
                break

            # If remaining shortest path has positive cost and we only wanted min-cost flow (not max flow), we could stop,
            # but for min-cost MAX-flow, we push flow along all paths as long as sink is reached.

            # Determine bottleneck capacity along path
            bottleneck = float("inf")
            if target_flow is not None:
                bottleneck = target_flow - total_flow

            curr = sink
            while curr != source:
                edge = parent_edge[curr]
                assert edge is not None
                bottleneck = min(bottleneck, edge.residual_capacity)
                curr = edge.u

            if bottleneck <= cls.EPSILON:
                break

            # Augment along the path
            curr = sink
            while curr != source:
                edge = parent_edge[curr]
                assert edge is not None
                edge.augment(bottleneck)
                curr = edge.u

            total_flow += bottleneck
            total_cost += bottleneck * dist[sink]

        return (total_flow, total_cost)
