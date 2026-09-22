import pytest

from algorithms.allocation import (allocate_min_cost_flow, greedy_set_cover,
                                   min_candidates_to_cover)


def test_allocate_min_cost_flow():
    candidates = [{"id": "c1"}, {"id": "c2"}]
    jobs = [
        {"id": "j1", "team_id": "t1", "headcount": 1},
        {"id": "j2", "team_id": "t1", "headcount": 1},
    ]
    teams = [{"id": "t1"}]
    fit_scores = {("c1", "j1"): 0.9, ("c2", "j2"): 0.8}

    assignments = allocate_min_cost_flow(candidates, jobs, teams, fit_scores)
    assert ("c1", "j1") in assignments
    assert ("c2", "j2") in assignments
    assert len(assignments) == 2


def test_min_candidates_to_cover():
    skills = ["python", "java"]
    masks = [1, 2]  # c0 has python(1), c1 has java(2)
    chosen = min_candidates_to_cover(skills, masks)
    assert chosen == [0, 1] or chosen == [1, 0]

    masks_infeasible = [1, 1]
    assert min_candidates_to_cover(skills, masks_infeasible) is None


def test_greedy_set_cover():
    skills = {"python", "java"}
    candidates = [
        {"id": "c1", "skills": ["python"], "cost": 1.0},
        {"id": "c2", "skills": ["python", "java"], "cost": 1.5},
    ]

    def cost_fn(c):
        return c["cost"]

    res = greedy_set_cover(skills, candidates, cost_fn)
    assert res["chosen"][0]["id"] == "c2"
    assert not res["residual_uncovered"]
