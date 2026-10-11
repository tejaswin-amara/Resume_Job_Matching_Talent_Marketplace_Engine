"""MarketplaceFlowNetwork: Talent allocation via network flow bipartite matching.

Models Source -> Candidates -> Jobs -> Sink with capacity and eligibility constraints.
Zero-library constraint: built strictly on CustomAdjacencyGraph and DinicAlgorithm.
"""

from typing import Any, NamedTuple

from core.engine.flow.dinic import DinicAlgorithm
from core.engine.structures.adjacency_graph import CustomAdjacencyGraph


class Assignment(NamedTuple):
    """Assignment of a candidate to a job."""

    candidate_id: Any
    job_id: Any
    score: float


class AllocationResult(NamedTuple):
    """Overall result of market flow allocation."""

    total_matches: int
    assignments: list[Assignment]


class CandidateNode:
    """Represents a candidate in the flow network."""

    def __init__(
        self,
        candidate_id: Any,
        skills: list[str] | None = None,
        capacity: int = 1,
    ) -> None:
        self.candidate_id = candidate_id
        self.skills = skills or []
        self.capacity = capacity


class JobNode:
    """Represents a job posting in the flow network."""

    def __init__(
        self,
        job_id: Any,
        required_skills: list[str] | None = None,
        capacity: int = 1,
        headcount: int | None = None,
    ) -> None:
        self.job_id = job_id
        self.required_skills = required_skills or []
        self.capacity = headcount if headcount is not None else capacity
        self.headcount = self.capacity


class MarketplaceFlowNetwork:
    """Bipartite capacity-constrained flow network for talent marketplace allocation."""

    def __init__(self) -> None:
        self.graph: CustomAdjacencyGraph = CustomAdjacencyGraph()
        self.source_id: int = 0
        self.sink_id: int = 1
        self.candidate_map: dict[Any, int] = {}
        self.candidate_rev_map: dict[int, Any] = {}
        self.job_map: dict[Any, int] = {}
        self.job_rev_map: dict[int, Any] = {}
        self.candidate_skills: dict[Any, set[str]] = {}
        self.job_skills: dict[Any, set[str]] = {}
        self.edge_scores: dict[tuple[int, int], float] = {}

    @staticmethod
    def _resolve_job_capacity(j: Any) -> int:
        """Resolve job capacity respecting headcount or capacity across objects and dicts."""
        if hasattr(j, "headcount") and getattr(j, "headcount", None) is not None:
            return getattr(j, "headcount")
        if hasattr(j, "capacity") and getattr(j, "capacity", None) is not None:
            return getattr(j, "capacity")
        if hasattr(j, "get"):
            val = j.get("headcount")
            if val is not None:
                return val
            return j.get("capacity", 1)
        return 1

    def build_network(
        self,
        candidates: list[Any],
        jobs: list[Any],
        capacities: dict[Any, int] | None = None,
        match_scores: dict[tuple[Any, Any], float] | None = None,
    ) -> None:
        """Construct the flow network from candidates, jobs, and capacities."""
        self.graph = CustomAdjacencyGraph()
        self.candidate_map = {}
        self.candidate_rev_map = {}
        self.job_map = {}
        self.job_rev_map = {}
        self.candidate_skills = {}
        self.job_skills = {}
        self.edge_scores = {}
        self.source_id = 0
        self.graph.add_node(self.source_id)

        next_id = 2  # 0 is source, 1 is sink

        # Map candidates
        for c in candidates:
            cid = getattr(c, "candidate_id", None)
            if cid is None:
                cid = getattr(c, "id", None)
            if cid is None and hasattr(c, "get"):
                cid = c.get("candidate_id", c.get("id"))
            if cid is None:
                cid = c["candidate_id"]

            c_skills = set(
                getattr(c, "skills", None)
                or (c.get("skills") if hasattr(c, "get") else None)
                or []
            )
            c_cap = getattr(c, "capacity", None)
            if c_cap is None and hasattr(c, "get"):
                c_cap = c.get("capacity", 1)
            if c_cap is None:
                c_cap = 1

            node_id = next_id
            next_id += 1
            self.candidate_map[cid] = node_id
            self.candidate_rev_map[node_id] = cid
            self.candidate_skills[cid] = c_skills
            self.graph.add_edge(self.source_id, node_id, capacity=float(c_cap))

        # Map jobs
        job_map_obj: dict[Any, Any] = {}
        for j in jobs:
            jid = getattr(j, "job_id", None)
            if jid is None:
                jid = getattr(j, "id", None)
            if jid is None and hasattr(j, "get"):
                jid = j.get("job_id", j.get("id"))
            if jid is None:
                jid = j["job_id"]

            j_skills = set(
                getattr(j, "required_skills", None)
                or getattr(j, "skills", None)
                or (j.get("required_skills") if hasattr(j, "get") else None)
                or (j.get("skills") if hasattr(j, "get") else None)
                or []
            )
            job_cap = self._resolve_job_capacity(j)
            j_cap = job_cap
            if capacities:
                if jid in capacities:
                    j_cap = capacities[jid]
                elif str(jid) in capacities:
                    j_cap = capacities[str(jid)]

            node_id = next_id
            next_id += 1
            self.job_map[jid] = node_id
            self.job_rev_map[node_id] = jid
            self.job_skills[jid] = j_skills
            job_map_obj[jid] = j

        # Sink node
        self.sink_id = 1
        self.graph.add_node(self.sink_id)

        # Edges from Jobs to Sink
        for jid, j_node_id in self.job_map.items():
            job = job_map_obj[jid]
            job_cap = self._resolve_job_capacity(job)
            j_cap = job_cap
            if capacities:
                if jid in capacities:
                    j_cap = capacities[jid]
                elif str(jid) in capacities:
                    j_cap = capacities[str(jid)]
            self.graph.add_edge(j_node_id, self.sink_id, capacity=float(j_cap))

        # Edges from Candidates to Jobs
        for cid, c_node_id in self.candidate_map.items():
            c_skills = self.candidate_skills[cid]
            for jid, j_node_id in self.job_map.items():
                j_skills = self.job_skills[jid]

                score = 0.0
                if match_scores and (cid, jid) in match_scores:
                    score = match_scores[(cid, jid)]
                    is_eligible = score > 0.0
                elif not j_skills:
                    is_eligible = True
                    score = 1.0
                else:
                    overlap = len(c_skills & j_skills)
                    is_eligible = overlap > 0
                    score = overlap / len(j_skills) if j_skills else 1.0

                if is_eligible:
                    self.graph.add_edge(c_node_id, j_node_id, capacity=1.0)
                    self.edge_scores[(c_node_id, j_node_id)] = score

    build_flow_network = build_network

    def execute_allocation(
        self,
        candidates: list[Any],
        jobs: list[Any],
        capacities: dict[Any, int] | None = None,
        match_scores: dict[tuple[Any, Any], float] | None = None,
    ) -> AllocationResult:
        """Execute Dinic's algorithm to obtain optimal talent assignment."""
        self.build_network(candidates, jobs, capacities, match_scores)
        max_flow = DinicAlgorithm.compute_max_flow(self.graph, self.source_id, self.sink_id)

        assignments: list[Assignment] = []
        for cid, c_node_id in self.candidate_map.items():
            for edge in self.graph.get_edges(c_node_id):
                if edge.v in self.job_rev_map and edge.flow > 0.5:
                    jid = self.job_rev_map[edge.v]
                    score = self.edge_scores.get((c_node_id, edge.v), 1.0)
                    assignments.append(Assignment(candidate_id=cid, job_id=jid, score=score))

        return AllocationResult(total_matches=len(assignments), assignments=assignments)
