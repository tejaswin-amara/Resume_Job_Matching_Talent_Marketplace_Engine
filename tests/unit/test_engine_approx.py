"""Unit tests for Approximation Algorithms (DSA Module M5).

Verifies GreedySetCover, VertexCoverApproximation, and KnapsackFPTAS.
"""

from core.engine.approx.greedy_set_cover import (
    CandidateSkillProfile,
    GreedySetCover,
)
from core.engine.approx.knapsack_fptas import (
    HiringCandidate,
    KnapsackFPTAS,
)
from core.engine.approx.vertex_cover import VertexCoverApproximation

# ==============================================================================
# 1. GreedySetCover Tests
# ==============================================================================


def test_greedy_set_cover_team_assembly():
    candidates = [
        CandidateSkillProfile("cand_A", ["python", "fastapi"], cost=10.0),
        CandidateSkillProfile("cand_B", ["react", "typescript"], cost=10.0),
        CandidateSkillProfile("cand_C", ["docker", "kubernetes", "postgres"], cost=15.0),
        CandidateSkillProfile("cand_D", ["python", "react"], cost=20.0),
    ]

    target = {"python", "fastapi", "react", "typescript", "docker"}
    result = GreedySetCover.find_minimum_team(candidates, target)

    assert result.uncovered_skills == set()
    assert result.covered_skills == target
    selected_ids = {c.candidate_id for c in result.selected_candidates}
    # Should choose A, B, and C rather than inefficient redundant candidate D
    assert "cand_A" in selected_ids
    assert "cand_B" in selected_ids
    assert "cand_C" in selected_ids


def test_greedy_set_cover_uncoverable_skills():
    candidates = [
        CandidateSkillProfile("cand_1", ["python"], cost=5.0),
    ]
    target = {"python", "quantum_computing"}
    res = GreedySetCover.find_minimum_team(candidates, target)

    assert res.covered_skills == {"python"}
    assert res.uncovered_skills == {"quantum_computing"}
    assert len(res.selected_candidates) == 1


# ==============================================================================
# 2. VertexCoverApproximation Tests
# ==============================================================================


def test_vertex_cover_approximation():
    # Triangle graph (0, 1), (1, 2), (2, 0)
    # OPT is 2. 2-approx selects at most 2 * OPT = 4 (in this case 2 endpoints of one edge = 2)
    edges = [(0, 1), (1, 2), (2, 0)]
    cover = VertexCoverApproximation.approximate_vertex_cover(3, edges)

    # Must cover all edges
    for u, v in edges:
        assert u in cover or v in cover

    assert len(cover) <= 2 * 2


def test_resolve_interview_conflicts():
    conflicts = [("interviewer_1", "candidate_A"), ("interviewer_1", "candidate_B")]
    rescheduled = VertexCoverApproximation.resolve_interview_conflicts(conflicts)
    assert len(rescheduled) > 0


# ==============================================================================
# 3. KnapsackFPTAS Tests
# ==============================================================================


def test_knapsack_fptas_budget_hiring():
    candidates = [
        HiringCandidate("c1", cost=10.0, value=60.0),
        HiringCandidate("c2", cost=20.0, value=100.0),
        HiringCandidate("c3", cost=30.0, value=120.0),
    ]
    budget = 50.0  # OPT: take c2 and c3 (cost 50, value 220)

    result = KnapsackFPTAS.solve(candidates, budget=budget, epsilon=0.1)

    assert result.total_cost <= budget
    # Must achieve at least (1 - 0.1) * 220 = 198.0
    assert result.total_value >= 198.0
    assert len(result.selected_candidates) >= 2


def test_knapsack_fptas_edge_cases():
    candidates = [
        HiringCandidate("c1", cost=100.0, value=50.0),
    ]
    # Insufficient budget
    res = KnapsackFPTAS.solve(candidates, budget=10.0)
    assert res.selected_candidates == []
    assert res.total_cost == 0.0
    assert res.total_value == 0.0
