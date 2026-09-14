import pytest
from algorithms.scoring import (
    propagation_credit,
    OntologyDistanceTable,
    seniority_penalty,
    lookup_historical_acceptance,
    recency_score,
    cosine,
    fit_score
)

def test_propagation_credit():
    assert propagation_credit(0) == 1.0
    assert propagation_credit(1) == 0.6
    assert propagation_credit(2) == 0.3
    assert propagation_credit(3) == 0.0

def test_ontology_distance_table():
    table = OntologyDistanceTable()
    table.add_distance("s1", "s2", 1)

    assert table.lookup("s1", "s1") == 0
    assert table.lookup("s1", "s2") == 1
    assert table.lookup("s2", "s1") == 1
    assert table.lookup("s1", "s3") == 999

def test_dummies():
    assert seniority_penalty({}, {}) == 1.0
    assert lookup_historical_acceptance("a", "b") == 0.5
    assert recency_score("now") == 1.0

def test_cosine():
    assert cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0

def test_fit_score():
    table = OntologyDistanceTable()
    table.add_distance("python", "java", 2)

    job = {
        'required_skills': [
            {'canonical_skill_id': 'python', 'weight': 1.0, 'hard_constraint': True, 'min_years': 2},
            {'canonical_skill_id': 'aws', 'weight': 0.5, 'hard_constraint': False}
        ],
        'embedding_vector': [1.0, 0.0],
        'profile_cluster': 'a'
    }

    candidate = {
        'skills': [
            {'canonical_skill_id': 'python', 'years_experience': 3},
            {'canonical_skill_id': 'aws', 'years_experience': 1}
        ],
        'embedding_vector': [1.0, 0.0],
        'profile_cluster': 'a',
        'parsed_at': 'now'
    }

    weights = {
        'hard': 0.3,
        'soft': 0.15,
        'depth': 0.1,
        'semantic': 0.15,
        'seniority': 0.1,
        'location': 0.05,
        'historical': 0.1,
        'recency': 0.05
    }

    score, expl = fit_score(candidate, job, table, weights)

    assert score > 0.0
    assert expl['hard_skill_coverage'] == 1.0
    assert expl['soft_skill_coverage'] == 1.0 # 0.5/0.5 = 1.0
    assert expl['semantic_similarity'] == 1.0
    assert len(expl['matched']) == 2
