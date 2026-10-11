import pytest
from core.engine.flow.marketplace_network import MarketplaceFlowNetwork


def test_marketplace_flow_reset():
    net = MarketplaceFlowNetwork()

    # Run once
    candidates1 = [{"id": "c1", "skills": ["python"], "experience_years": 5}]
    jobs1 = [{"id": "j1", "skills": ["python"], "headcount": 1}]
    net.build_network(candidates1, jobs1)

    # Check maps
    assert "c1" in net.candidate_map

    # Run twice
    candidates2 = [{"id": "c2", "skills": ["java"], "experience_years": 5}]
    jobs2 = [{"id": "j2", "skills": ["java"], "headcount": 1}]
    net.build_network(candidates2, jobs2)

    # Check maps
    assert "c1" not in net.candidate_map
    assert "c2" in net.candidate_map
