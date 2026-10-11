"""BitmaskTSP: Exact Traveling Salesperson Problem solver via O(2^n * n^2) Dynamic Programming.

Used for optimal recruiter multi-office/candidate interview routing.
Zero-library constraint: built strictly with primitive arrays and bitwise operators.
"""


class BitmaskTSP:
    """Exact TSP and Hamiltonian path solver via bitmask dynamic programming."""

    INF: float = float("inf")

    @classmethod
    def find_optimal_tour(
        cls,
        cost_matrix: list[list[float]],
        start_node: int = 0,
    ) -> tuple[float, list[int]]:
        """Find the minimum-cost closed tour starting and ending at start_node visiting all nodes.

        Returns (min_cost, path) where path begins and ends at start_node.
        Complexity: O(2^n * n^2) time and O(2^n * n) space.
        """
        n = len(cost_matrix)
        if n == 0:
            return (0.0, [])
        if n == 1:
            return (0.0, [start_node, start_node])

        num_states = 1 << n
        dp: list[list[float]] = [[cls.INF] * n for _ in range(num_states)]
        parent: list[list[int]] = [[-1] * n for _ in range(num_states)]

        initial_mask = 1 << start_node
        dp[initial_mask][start_node] = 0.0

        for mask in range(num_states):
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                curr_cost = dp[mask][u]
                if curr_cost == cls.INF:
                    continue

                for v in range(n):
                    if not (mask & (1 << v)):
                        next_mask = mask | (1 << v)
                        cand_cost = curr_cost + cost_matrix[u][v]
                        if cand_cost < dp[next_mask][v]:
                            dp[next_mask][v] = cand_cost
                            parent[next_mask][v] = u

        # Complete the tour by returning to start_node
        full_mask = num_states - 1
        best_cost = cls.INF
        last_node = -1

        for u in range(n):
            if u != start_node:
                tour_cost = dp[full_mask][u] + cost_matrix[u][start_node]
                if tour_cost < best_cost:
                    best_cost = tour_cost
                    last_node = u

        if last_node == -1 or best_cost == cls.INF:
            return (cls.INF, [])

        # Reconstruct path backwards
        path: list[int] = [start_node]
        curr_mask = full_mask
        curr_node = last_node

        while curr_node != -1 and curr_mask > 0:
            if curr_node != start_node:
                path.append(curr_node)
            prev_node = parent[curr_mask][curr_node]
            curr_mask ^= 1 << curr_node
            curr_node = prev_node

        path.append(start_node)
        path.reverse()
        return (best_cost, path)

    @classmethod
    def find_optimal_path(
        cls,
        cost_matrix: list[list[float]],
        start_node: int = 0,
    ) -> tuple[float, list[int]]:
        """Find the minimum-cost open Hamiltonian path visiting every node without returning."""
        n = len(cost_matrix)
        if n == 0:
            return (0.0, [])
        if n == 1:
            return (0.0, [start_node])

        num_states = 1 << n
        dp: list[list[float]] = [[cls.INF] * n for _ in range(num_states)]
        parent: list[list[int]] = [[-1] * n for _ in range(num_states)]

        initial_mask = 1 << start_node
        dp[initial_mask][start_node] = 0.0

        for mask in range(num_states):
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                curr_cost = dp[mask][u]
                if curr_cost == cls.INF:
                    continue

                for v in range(n):
                    if not (mask & (1 << v)):
                        next_mask = mask | (1 << v)
                        cand_cost = curr_cost + cost_matrix[u][v]
                        if cand_cost < dp[next_mask][v]:
                            dp[next_mask][v] = cand_cost
                            parent[next_mask][v] = u

        full_mask = num_states - 1
        best_cost = cls.INF
        last_node = -1

        for u in range(n):
            if dp[full_mask][u] < best_cost:
                best_cost = dp[full_mask][u]
                last_node = u

        if last_node == -1 or best_cost == cls.INF:
            return (cls.INF, [])

        path: list[int] = []
        curr_mask = full_mask
        curr_node = last_node

        while curr_node != -1 and curr_mask > 0:
            path.append(curr_node)
            prev_node = parent[curr_mask][curr_node]
            curr_mask ^= 1 << curr_node
            curr_node = prev_node

        path.reverse()
        return (best_cost, path)
