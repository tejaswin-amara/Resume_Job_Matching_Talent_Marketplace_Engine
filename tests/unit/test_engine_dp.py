"""Unit tests for Advanced Dynamic Programming Algorithms (DSA Module M3).

Verifies WagnerFischer, SequenceAlignment, BitmaskTSP, SOSDynamicProgramming, and TreeRerootingDP.
"""

from core.engine.dp.bitmask_tsp import BitmaskTSP
from core.engine.dp.sequence_alignment import SequenceAlignment
from core.engine.dp.sos_dp import SkillDensityIndex, SOSDynamicProgramming
from core.engine.dp.tree_rerooting import TreeRerootingDP
from core.engine.dp.wagner_fischer import WagnerFischer

# ==============================================================================
# 1. WagnerFischer Tests
# ==============================================================================


def test_wagner_fischer_levenshtein():
    assert WagnerFischer.levenshtein_distance("kitten", "sitting") == 3
    assert WagnerFischer.levenshtein_distance("flaw", "lawn") == 2
    assert WagnerFischer.levenshtein_distance("", "python") == 6
    assert WagnerFischer.levenshtein_distance("same", "same") == 0


def test_wagner_fischer_damerau_transposition():
    # "teh" -> "the" requires 1 transposition in Damerau, but 2 edits in standard Levenshtein
    assert WagnerFischer.levenshtein_distance("teh", "the") == 2
    assert WagnerFischer.damerau_levenshtein_distance("teh", "the") == 1

    # CA -> AC
    assert WagnerFischer.damerau_levenshtein_distance("CA", "AC") == 1


def test_wagner_fischer_domain_weighted():
    # "react" vs "reakt": 'c' and 'k' have domain substitution cost 0.4
    dist_phonetic = WagnerFischer.domain_weighted_distance("react", "reakt")
    assert abs(dist_phonetic - 0.4) < 1e-6

    # Normalization
    sim = WagnerFischer.normalized_similarity("react", "reakt", algorithm="weighted")
    assert sim > 0.90
    assert WagnerFischer.normalized_similarity("abc", "abc") == 1.0


# ==============================================================================
# 2. SequenceAlignment Tests (Needleman-Wunsch & Smith-Waterman)
# ==============================================================================


def test_sequence_alignment_global_career_path():
    sa = SequenceAlignment(match_score=2.0, mismatch_penalty=-1.0, gap_penalty=-1.0)
    c1 = ["Intern", "Junior", "Mid", "Senior", "Lead"]
    c2 = ["Junior", "Senior", "Lead"]

    res = sa.needleman_wunsch(c1, c2)
    assert res.score > 0
    assert len(res.aligned_seq1) == len(res.aligned_seq2)
    assert "Junior" in res.aligned_seq2
    assert "Senior" in res.aligned_seq2
    assert "Lead" in res.aligned_seq2


def test_sequence_alignment_local_smith_waterman():
    sa = SequenceAlignment(match_score=3.0, mismatch_penalty=-2.0, gap_penalty=-2.0)
    s1 = "HEAGAWGHEE"
    s2 = "PAWHEAE"

    res = sa.smith_waterman(s1, s2)
    assert res.score >= 6.0  # Found matching local substring "AWGHE" / "AWHE"


# ==============================================================================
# 3. BitmaskTSP Tests
# ==============================================================================


def test_bitmask_tsp_exact_tour():
    # 4 cities with symmetric distance matrix
    # Optimal tour: 0 -> 1 -> 3 -> 2 -> 0: 10 + 25 + 30 + 15 = 80
    matrix = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0],
    ]
    cost, tour = BitmaskTSP.find_optimal_tour(matrix, start_node=0)
    assert cost == 80.0
    assert tour[0] == 0 and tour[-1] == 0
    assert len(set(tour[:-1])) == 4


def test_bitmask_tsp_open_path():
    # Linear path: 0 -> 1 -> 2
    matrix = [
        [0, 5, 20],
        [5, 0, 7],
        [20, 7, 0],
    ]
    cost, path = BitmaskTSP.find_optimal_path(matrix, start_node=0)
    assert cost == 12.0
    assert path == [0, 1, 2]


# ==============================================================================
# 4. SOSDynamicProgramming Tests (Yates' Technique)
# ==============================================================================


def test_sos_dp_subset_sums():
    # 3 bits: 8 elements [A[0], A[1], ..., A[7]]
    A = [1, 2, 4, 8, 16, 32, 64, 128]
    # mask 0: sub={0} -> 1
    # mask 1 (001): sub={0, 1} -> 1 + 2 = 3
    # mask 3 (011): sub={0, 1, 2, 3} -> 1 + 2 + 4 + 8 = 15
    # mask 7 (111): all elements -> sum(A) = 255
    F = SOSDynamicProgramming.compute_subsets_sum(A, num_bits=3)
    assert F[0] == 1
    assert F[1] == 3
    assert F[3] == 15
    assert F[7] == 255


def test_sos_dp_skill_density_index():
    index = SkillDensityIndex(num_skills=4)
    # Skills: 0: Python, 1: FastAPI, 2: SQL, 3: Docker
    # Candidate 1: Python + FastAPI + SQL (mask = 1 + 2 + 4 = 7)
    # Candidate 2: Python + SQL (mask = 1 + 4 = 5)
    # Candidate 3: Python + FastAPI + SQL + Docker (mask = 15)
    index.add_candidate_mask(7)
    index.add_candidate_mask(5)
    index.add_candidate_mask(15)
    index.build_index()

    # Query: how many candidates have at least Python + SQL (mask 5)?
    # Candidates 1, 2, and 3 all have at least mask 5!
    assert index.count_candidates_with_all_skills(5) == 3

    # Query: how many have at least Docker (mask 8)?
    # Only candidate 3 (mask 15) has bit 3
    assert index.count_candidates_with_all_skills(8) == 1

    # Query: how many have at least FastAPI + Docker (mask 2 + 8 = 10)?
    assert index.count_candidates_with_all_skills(10) == 1


# ==============================================================================
# 5. TreeRerootingDP Tests
# ==============================================================================


def test_tree_rerooting_star_and_line():
    # Star tree with node 0 at center, connected to 1, 2, 3, 4
    # All distances from 0 to 1, 2, 3, 4 are 1 -> total = 4
    # All distances from 1 to 0 (1), to 2, 3, 4 (2 each) -> 1 + 2*3 = 7
    adj = [
        [1, 2, 3, 4],  # 0
        [0],  # 1
        [0],  # 2
        [0],  # 3
        [0],  # 4
    ]
    distances = TreeRerootingDP.compute_all_distances(adj)
    assert distances[0] == 4.0
    assert distances[1] == 7.0
    assert distances[2] == 7.0

    centroid = TreeRerootingDP.find_centroid(adj)
    assert centroid == 0

    report = TreeRerootingDP.balance_headcounts(adj, [10, 2, 2, 2, 2])
    assert report.centroid_node == 0
