"""DinicAlgorithm: Level Graph BFS + Blocking Flow DFS with Edge Pruning in O(V^2 * E).

Zero-library constraint: built strictly with primitive arrays, pointer index arrays,
and DFS backtracking.
"""

from core.engine.structures.adjacency_graph import CustomAdjacencyGraph


class DinicAlgorithm:
    """Dinic's maximum flow algorithm with level graphs and edge pruning."""

    EPSILON: float = 1e-9

    @classmethod
    def compute_max_flow(cls, graph: CustomAdjacencyGraph, source: int, sink: int) -> float:
        """Compute maximum flow from source to sink in O(V^2 * E) time."""
        if source == sink:
            return 0.0
        total_flow = 0.0
        num_nodes = max(graph.nodes() + [source, sink]) + 1

        level = [-1] * num_nodes
        work = [0] * num_nodes

        def bfs_level_graph() -> bool:
            """Construct level graph using BFS."""
            for i in range(num_nodes):
                level[i] = -1

            level[source] = 0
            queue: list[int] = [source]
            head = 0

            while head < len(queue):
                u = queue[head]
                head += 1

                for edge in graph.get_edges(u):
                    v = edge.v
                    if level[v] < 0 and edge.residual_capacity > cls.EPSILON:
                        level[v] = level[u] + 1
                        queue.append(v)

            return level[sink] >= 0

        def dfs_blocking_flow(u: int, pushed: float) -> float:
            """Find blocking flow in level graph with work pointer edge pruning."""
            if u == sink or pushed <= cls.EPSILON:
                return pushed

            edges = graph.get_edges(u)
            while work[u] < len(edges):
                edge = edges[work[u]]
                v = edge.v

                if level[v] == level[u] + 1 and edge.residual_capacity > cls.EPSILON:
                    tr = dfs_blocking_flow(v, min(pushed, edge.residual_capacity))
                    if tr > cls.EPSILON:
                        edge.augment(tr)
                        return tr

                # Prune saturated or dead-end edge
                work[u] += 1

            return 0.0

        while bfs_level_graph():
            for i in range(num_nodes):
                work[i] = 0

            while True:
                pushed = dfs_blocking_flow(source, float("inf"))
                if pushed <= cls.EPSILON:
                    break
                total_flow += pushed

        return total_flow
