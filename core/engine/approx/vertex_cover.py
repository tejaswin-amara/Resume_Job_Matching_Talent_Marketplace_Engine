"""VertexCoverApproximation: 2-approximation via maximal matching for conflict resolution.

Identifies minimal intervention set to resolve candidate-interviewer scheduling conflicts.
Guarantees size <= 2 * OPT.
Zero-library constraint: built strictly on primitive arrays and sets.
"""

from collections.abc import Sequence
from typing import Any


class VertexCoverApproximation:
    """2-Approximation Vertex Cover algorithm based on maximal disjoint edge matching."""

    @classmethod
    def approximate_vertex_cover(
        cls,
        num_vertices: int,
        edges: Sequence[tuple[int, int]],
    ) -> list[int]:
        """Compute 2-approximation of minimum vertex cover for integer-indexed graph.

        Returns list of vertex indices in the cover.
        """
        in_cover = [False] * num_vertices
        cover: list[int] = []

        for u, v in edges:
            if 0 <= u < num_vertices and 0 <= v < num_vertices:
                # If neither endpoint is already covered, take both endpoints
                if not in_cover[u] and not in_cover[v]:
                    in_cover[u] = True
                    in_cover[v] = True
                    cover.append(u)
                    cover.append(v)

        return sorted(cover)

    @classmethod
    def resolve_interview_conflicts(
        cls,
        conflicts: Sequence[tuple[Any, Any]],
    ) -> set[Any]:
        """Given a list of conflicting pairs (e.g. overlapping interviews),

        find a 2-approximate minimum set of events/nodes to reschedule to eliminate all conflicts.
        """
        cover: set[Any] = set()

        for u, v in conflicts:
            if u not in cover and v not in cover:
                cover.add(u)
                cover.add(v)

        return cover
