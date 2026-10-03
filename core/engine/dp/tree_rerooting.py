"""TreeRerootingDP: O(V) All-Roots Tree Dynamic Programming.

Used for finding organizational centroids, optimal executive reporting hubs,
and balancing departmental communication latencies.
Zero-library constraint: built strictly with primitive arrays and recursion/stack pointers.
"""

from typing import NamedTuple


class OrgBalanceReport(NamedTuple):
    """Report on organizational tree balance and communication latencies."""

    centroid_node: int
    min_total_latency: float
    all_node_latencies: list[float]
    total_headcount: int


class TreeRerootingDP:
    """Tree Dynamic Programming with Rerooting in strictly O(V) linear time."""

    @classmethod
    def compute_all_distances(
        cls,
        adj: list[list[int]],
        headcounts: list[int] | None = None,
    ) -> list[float]:
        """Compute sum of weighted distances from every node to all other nodes in O(V) time."""
        n = len(adj)
        if n == 0:
            return []
        if n == 1:
            return [0.0]

        weights = headcounts if headcounts is not None else [1] * n
        total_weight = sum(weights)

        # Subtree weights and subtree distance sums
        subtree_weight = [0] * n
        subtree_dist = [0.0] * n

        # Post-order DFS from node 0 (simulated or recursive)
        # Using iterative post-order traversal to prevent recursion depth issues
        visited = [False] * n
        parent = [-1] * n
        order: list[int] = []

        stack = [0]
        visited[0] = True

        while stack:
            u = stack.pop()
            order.append(u)
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    stack.append(v)

        # Bottom-up pass in reverse topological order
        for u in reversed(order):
            w = weights[u]
            d = 0.0
            for v in adj[u]:
                if parent[v] == u:
                    w += subtree_weight[v]
                    d += subtree_dist[v] + float(subtree_weight[v])
            subtree_weight[u] = w
            subtree_dist[u] = d

        # Pre-order rerooting pass
        ans = [0.0] * n
        ans[0] = subtree_dist[0]

        # BFS / queue to push down answers from parent to children
        queue = [0]
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1

            for v in adj[u]:
                if parent[v] == u:
                    # Reroot from u to v:
                    # Subtract subtree_weight[v] contribution
                    # Add (total_weight - subtree_weight[v]) contribution
                    ans[v] = (
                        ans[u] - float(subtree_weight[v]) + float(total_weight - subtree_weight[v])
                    )
                    queue.append(v)

        return ans

    @classmethod
    def find_centroid(
        cls,
        adj: list[list[int]],
        headcounts: list[int] | None = None,
    ) -> int:
        """Find the organizational centroid (node minimizing maximum partitioned component size)."""
        n = len(adj)
        if n <= 1:
            return 0

        weights = headcounts if headcounts is not None else [1] * n
        total_weight = sum(weights)

        # Bottom-up subtree weights
        visited = [False] * n
        parent = [-1] * n
        order: list[int] = []

        stack = [0]
        visited[0] = True
        while stack:
            u = stack.pop()
            order.append(u)
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    stack.append(v)

        subtree_weight = [0] * n
        for u in reversed(order):
            w = weights[u]
            for v in adj[u]:
                if parent[v] == u:
                    w += subtree_weight[v]
            subtree_weight[u] = w

        best_centroid = 0
        min_max_component = float("inf")

        for u in range(n):
            max_comp = 0
            for v in adj[u]:
                if parent[v] == u:
                    max_comp = max(max_comp, subtree_weight[v])
                elif parent[u] == v:
                    max_comp = max(max_comp, total_weight - subtree_weight[u])
            if max_comp < min_max_component:
                min_max_component = max_comp
                best_centroid = u

        return best_centroid

    @classmethod
    def balance_headcounts(
        cls,
        adj: list[list[int]],
        headcounts: list[int],
    ) -> OrgBalanceReport:
        """Analyze organizational tree and identify the optimal central communication hub."""
        latencies = cls.compute_all_distances(adj, headcounts)
        centroid = cls.find_centroid(adj, headcounts)

        min_latency = min(latencies) if latencies else 0.0
        # If there's a tie or centroid minimizes latency, pick argmin
        argmin_node = min(range(len(latencies)), key=lambda i: latencies[i]) if latencies else 0

        return OrgBalanceReport(
            centroid_node=argmin_node,
            min_total_latency=min_latency,
            all_node_latencies=latencies,
            total_headcount=sum(headcounts) if headcounts else len(adj),
        )
