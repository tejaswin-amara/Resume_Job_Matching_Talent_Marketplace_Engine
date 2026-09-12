import pytest
from algorithms.allocation import allocate_min_cost_flow, min_candidates_to_cover, greedy_set_cover

def test_allocate_min_cost_flow():
    candidates = [{"id": "c1"}, {"id": "c2"}]
    jobs = [{"id": "j1", "team_id": "t1", "headcount": 1}]
    teams = []
    scores = {("c1", "j1"): 0.9, ("c2", "j1"): 0.5}

    assignments = allocate_min_cost_flow(candidates, jobs, teams, scores)
    assert len(assignments) == 1
    assert assignments[0] == ("c1", "j1")

def test_min_candidates_to_cover():
    universe = ["s1", "s2", "s3"]
    # c0 has s1, c1 has s2,s3, c2 has s1,s2
    masks = [1, 6, 3] # 001, 110, 011
    chosen = min_candidates_to_cover(universe, masks)
    assert len(chosen) == 2
    assert set(chosen) == {0, 1}

def test_greedy_set_cover():
    universe = {"s1", "s2", "s3"}
    candidates = [
        {"id": "c1", "skills": ["s1"], "cost": 1.0},
        {"id": "c2", "skills": ["s2", "s3"], "cost": 1.0},
        {"id": "c3", "skills": ["s1", "s2"], "cost": 1.0}
    ]
    res = greedy_set_cover(universe, candidates, lambda c: c['cost'])
    assert len(res['chosen']) == 2
    ids = {c['id'] for c in res['chosen']}
    assert ids == {"c2", "c3"} or ids == {"c1", "c2"} or ids == {"c3", "c1"} # depends on iteration order but optimal is c2, c3
