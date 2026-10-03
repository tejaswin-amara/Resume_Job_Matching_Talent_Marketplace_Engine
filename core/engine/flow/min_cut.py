"""MinCutAnalyzer: Min s-t cut identification for talent pipeline bottleneck diagnosis.

Computes the minimum cut from residual network reachability via BFS and identifies
critical saturated constraint edges and bottleneck skills.
Zero-library constraint: built strictly on primitive BFS and set operations.
"""

from typing import NamedTuple

from core.engine.flow.marketplace_network import MarketplaceFlowNetwork
from core.engine.structures.adjacency_graph import FlowEdge


class BottleneckReport(NamedTuple):
    """Bottleneck diagnostics derived from minimum s-t cut."""

    saturated_edges: list[FlowEdge]
    cut_capacity: float
    bottleneck_skills: list[str]


class MinCutAnalyzer:
    """Min-Cut analyzer for residual flow networks."""

    EPSILON: float = 1e-9

    @classmethod
    def compute_min_cut_partitions(
        cls,
        network: MarketplaceFlowNetwork,
    ) -> tuple[set[int], set[int]]:
        """Compute (S, T) partitions from source reachability in residual network."""
        graph = network.graph
        source = network.source_id

        # BFS in residual network (edges with residual capacity > 0)
        s_partition: set[int] = set()
        queue: list[int] = [source]
        s_partition.add(source)
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1

            for edge in graph.get_edges(u):
                if edge.residual_capacity > cls.EPSILON and edge.v not in s_partition:
                    s_partition.add(edge.v)
                    queue.append(edge.v)

        all_nodes = set(graph.nodes()) | {network.source_id, network.sink_id}
        t_partition = all_nodes - s_partition

        return (s_partition, t_partition)

    @classmethod
    def find_bottlenecks(cls, network: MarketplaceFlowNetwork) -> BottleneckReport:
        """Analyze minimum s-t cut and identify bottleneck saturated edges and skill deficits."""
        s_partition, t_partition = cls.compute_min_cut_partitions(network)

        graph = network.graph
        saturated_edges: list[FlowEdge] = []
        cut_capacity = 0.0
        bottleneck_skills_set: set[str] = set()

        # Edges from S to T that are saturated in original graph
        for u in s_partition:
            for edge in graph.get_edges(u):
                if edge.v in t_partition and edge.capacity > 0:
                    if edge.residual_capacity <= cls.EPSILON:
                        saturated_edges.append(edge)
                        cut_capacity += edge.capacity

                        # Check if edge is from candidate to job or job to sink
                        if edge.v in network.job_rev_map:
                            jid = network.job_rev_map[edge.v]
                            for sk in network.job_skills.get(jid, set()):
                                bottleneck_skills_set.add(sk)
                        elif u in network.job_rev_map:
                            jid = network.job_rev_map[u]
                            for sk in network.job_skills.get(jid, set()):
                                bottleneck_skills_set.add(sk)

                        if edge.v in network.candidate_rev_map:
                            cid = network.candidate_rev_map[edge.v]
                            for sk in network.candidate_skills.get(cid, set()):
                                bottleneck_skills_set.add(sk)
                        elif u in network.candidate_rev_map:
                            cid = network.candidate_rev_map[u]
                            for sk in network.candidate_skills.get(cid, set()):
                                bottleneck_skills_set.add(sk)

        return BottleneckReport(
            saturated_edges=saturated_edges,
            cut_capacity=cut_capacity,
            bottleneck_skills=sorted(list(bottleneck_skills_set)),
        )
