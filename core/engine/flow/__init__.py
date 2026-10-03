"""Network Flow algorithms.

Zero-library constraint: built strictly from primitive arrays and pointer loops.
"""

from core.engine.flow.dinic import DinicAlgorithm
from core.engine.flow.edmonds_karp import EdmondsKarp
from core.engine.flow.marketplace_network import (
    AllocationResult,
    Assignment,
    CandidateNode,
    JobNode,
    MarketplaceFlowNetwork,
)
from core.engine.flow.min_cost_max_flow import MinCostMaxFlow
from core.engine.flow.min_cut import BottleneckReport, MinCutAnalyzer

__all__ = [
    "AllocationResult",
    "Assignment",
    "BottleneckReport",
    "CandidateNode",
    "DinicAlgorithm",
    "EdmondsKarp",
    "JobNode",
    "MarketplaceFlowNetwork",
    "MinCostMaxFlow",
    "MinCutAnalyzer",
]
