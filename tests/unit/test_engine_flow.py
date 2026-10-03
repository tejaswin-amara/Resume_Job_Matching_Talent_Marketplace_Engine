"""Unit tests for Network Flow Algorithms (DSA Module M4).

Verifies EdmondsKarp, DinicAlgorithm, MarketplaceFlowNetwork, MinCutAnalyzer, and MinCostMaxFlow.
"""

from core.engine.flow.dinic import DinicAlgorithm
from core.engine.flow.edmonds_karp import EdmondsKarp
from core.engine.flow.marketplace_network import (
    CandidateNode,
    JobNode,
    MarketplaceFlowNetwork,
)
from core.engine.flow.min_cost_max_flow import MinCostMaxFlow
from core.engine.flow.min_cut import MinCutAnalyzer
from core.engine.structures.adjacency_graph import CustomAdjacencyGraph

# ==============================================================================
# Helper to build classic textbook max-flow network
# ==============================================================================


def build_classic_flow_network() -> tuple[CustomAdjacencyGraph, int, int]:
    """Build classic 6-node network: s=0, t=5. Max flow is known to be 23.0."""
    g = CustomAdjacencyGraph()
    # 0 -> 1 (16), 0 -> 2 (13)
    # 1 -> 2 (10), 1 -> 3 (12)
    # 2 -> 1 (4), 2 -> 4 (14)
    # 3 -> 2 (9), 3 -> 5 (20)
    # 4 -> 3 (7), 4 -> 5 (4)
    g.add_edge(0, 1, 16.0)
    g.add_edge(0, 2, 13.0)
    g.add_edge(1, 2, 10.0)
    g.add_edge(1, 3, 12.0)
    g.add_edge(2, 1, 4.0)
    g.add_edge(2, 4, 14.0)
    g.add_edge(3, 2, 9.0)
    g.add_edge(3, 5, 20.0)
    g.add_edge(4, 3, 7.0)
    g.add_edge(4, 5, 4.0)
    return g, 0, 5


# ==============================================================================
# 1. Edmonds-Karp & Dinic Max Flow Tests
# ==============================================================================


def test_edmonds_karp_max_flow():
    g, s, t = build_classic_flow_network()
    max_flow = EdmondsKarp.compute_max_flow(g, s, t)
    assert abs(max_flow - 23.0) < 1e-6


def test_dinic_max_flow():
    g, s, t = build_classic_flow_network()
    max_flow = DinicAlgorithm.compute_max_flow(g, s, t)
    assert abs(max_flow - 23.0) < 1e-6


# ==============================================================================
# 2. MarketplaceFlowNetwork Tests
# ==============================================================================


def test_marketplace_flow_network_allocation():
    candidates = [
        CandidateNode(candidate_id="c1", skills=["python", "fastapi"]),
        CandidateNode(candidate_id="c2", skills=["react", "typescript"]),
        CandidateNode(candidate_id="c3", skills=["python", "docker", "postgres"]),
    ]
    jobs = [
        JobNode(job_id="j1", required_skills=["python"], capacity=1),
        JobNode(job_id="j2", required_skills=["react"], capacity=1),
        JobNode(job_id="j3", required_skills=["docker"], capacity=1),
    ]

    net = MarketplaceFlowNetwork()
    result = net.execute_allocation(candidates, jobs)

    # All 3 candidates can be matched to the 3 distinct jobs
    assert result.total_matches == 3
    assigned_candidates = {a.candidate_id for a in result.assignments}
    assigned_jobs = {a.job_id for a in result.assignments}
    assert assigned_candidates == {"c1", "c2", "c3"}
    assert assigned_jobs == {"j1", "j2", "j3"}


def test_marketplace_capacity_constraints():
    # 4 candidates qualifying for only 1 job with capacity 2
    candidates = [CandidateNode(candidate_id=f"c{i}", skills=["python"]) for i in range(4)]
    jobs = [JobNode(job_id="j1", required_skills=["python"], capacity=2)]

    net = MarketplaceFlowNetwork()
    result = net.execute_allocation(candidates, jobs, capacities={"j1": 2})

    # Exactly 2 candidates should be allocated due to job capacity limit
    assert result.total_matches == 2
    assert len(result.assignments) == 2


# ==============================================================================
# 3. MinCutAnalyzer Tests (Max-Flow Min-Cut Theorem Verification)
# ==============================================================================


def test_min_cut_bottlenecks():
    candidates = [
        CandidateNode(candidate_id="c1", skills=["rust"]),
        CandidateNode(candidate_id="c2", skills=["python"]),
    ]
    # 3 jobs demanding python, but only 1 python candidate
    jobs = [
        JobNode(job_id="j1", required_skills=["python"], capacity=1),
        JobNode(job_id="j2", required_skills=["python"], capacity=1),
        JobNode(job_id="j3", required_skills=["python"], capacity=1),
    ]

    net = MarketplaceFlowNetwork()
    res = net.execute_allocation(candidates, jobs)
    assert res.total_matches == 1

    report = MinCutAnalyzer.find_bottlenecks(net)
    assert report.cut_capacity >= 1.0
    assert "python" in report.bottleneck_skills


# ==============================================================================
# 4. MinCostMaxFlow Tests
# ==============================================================================


def test_min_cost_max_flow():
    # Graph:
    # 0 -> 1 (cap 2, cost 1)
    # 0 -> 2 (cap 1, cost 2)
    # 1 -> 3 (cap 1, cost 3)
    # 2 -> 3 (cap 1, cost 1)
    # Total path 1: 0 -> 1 -> 3 (cap 1, cost 1 + 3 = 4)
    # Total path 2: 0 -> 2 -> 3 (cap 1, cost 2 + 1 = 3)
    # Max flow is 2. Path 2 is cheaper, so it carries 1 unit at cost 3; Path 1 carries 1 unit at cost 4.
    # Total cost = 3 + 4 = 7.
    g = CustomAdjacencyGraph()
    g.add_edge(0, 1, capacity=2.0, cost=1.0)
    g.add_edge(0, 2, capacity=1.0, cost=2.0)
    g.add_edge(1, 3, capacity=1.0, cost=3.0)
    g.add_edge(2, 3, capacity=1.0, cost=1.0)

    flow, cost = MinCostMaxFlow.compute_min_cost_max_flow(g, source=0, sink=3)
    assert abs(flow - 2.0) < 1e-6
    assert abs(cost - 7.0) < 1e-6
