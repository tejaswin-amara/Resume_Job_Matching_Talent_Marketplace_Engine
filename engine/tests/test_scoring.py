import pytest
from algorithms.scoring import fit_score, OntologyDistanceTable

def test_fit_score():
    candidate = {"skills": [{"canonical_skill_id": "s1", "years_experience": 2}]}
    job = {"required_skills": [{"canonical_skill_id": "s1", "weight": 1.0, "hard_constraint": True}]}
    dt = OntologyDistanceTable()
    dt.add_distance("s1", "s1", 0)

    score, expl = fit_score(candidate, job, dt, {"hard": 1.0})
    assert score > 0
    assert expl['hard_skill_coverage'] == 1.0

def test_fit_score_hard_fail():
    candidate = {"skills": [{"canonical_skill_id": "s2"}]}
    job = {"required_skills": [{"canonical_skill_id": "s1", "weight": 1.0, "hard_constraint": True}]}
    dt = OntologyDistanceTable()

    score, expl = fit_score(candidate, job, dt, {"hard": 1.0})
    assert score == 0.0
    assert expl == {}
