"""Approximation algorithms.

Zero-library constraint: built strictly from primitive arrays and sets.
"""

from core.engine.approx.greedy_set_cover import (
    CandidateSkillProfile,
    GreedySetCover,
    TeamCoverResult,
)
from core.engine.approx.knapsack_fptas import (
    HiringCandidate,
    KnapsackFPTAS,
    KnapsackResult,
)
from core.engine.approx.vertex_cover import VertexCoverApproximation

__all__ = [
    "CandidateSkillProfile",
    "GreedySetCover",
    "HiringCandidate",
    "KnapsackFPTAS",
    "KnapsackResult",
    "TeamCoverResult",
    "VertexCoverApproximation",
]
