import pytest
from core.engine.dp.bitmask_tsp import BitmaskTSP
from core.engine.dp.tree_rerooting import TreeRerootingDP


def test_tsp_asymmetric():
    # Asymmetric matrix test
    # 0 -> 1 = 1
    # 1 -> 0 = 10
    cost_matrix = [[0, 1], [10, 0]]
    cost, path = BitmaskTSP.find_optimal_tour(cost_matrix, start_node=0)
    assert cost == 11
    assert path == [0, 1, 0]


def test_tsp_arbitrary_start():
    # Start at 1
    cost_matrix = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0],
    ]
    cost, path = BitmaskTSP.find_optimal_tour(cost_matrix, start_node=1)
    assert cost == 80
    assert path[0] == 1
    assert path[-1] == 1


def test_tree_centroid():
    adj = [[1], [0, 2], [1, 3], [2]]
    headcounts = [1, 10, 1, 1]

    report = TreeRerootingDP.balance_headcounts(adj, headcounts)
    assert report.centroid_node == 1
