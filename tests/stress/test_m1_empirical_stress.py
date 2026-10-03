"""Empirical Stress Test Suite for Milestone 1 (Zero-Library Algorithmic Core).

Executed by challenger_m1_2 to empirically stress-test:
1. core/engine/dp:
   - Wagner-Fischer edit distance & domain-weighted variants
   - Needleman-Wunsch & Smith-Waterman sequence alignment (empty, single char, disjoint)
   - BitmaskTSP (n=12 performance, tour reconstruction integrity)
   - SOSDynamicProgramming (n=10 mask density, subset/superset sums vs brute-force oracle)
   - TreeRerootingDP (path, star, balanced tree, weighted headcounts vs BFS oracle)
2. core/engine/approx:
   - GreedySetCover (1 + ln n) approximation ratio vs exact B&B oracle
   - VertexCover 2-approximation vs exact vertex cover oracle
   - KnapsackFPTAS (1 - epsilon) optimality bound vs exact knapsack oracle
3. core/engine/randomised:
   - ReservoirSampler uniformity via Pearson Chi-Square goodness-of-fit test
   - Miller-Rabin known primes, Carmichael numbers, Mersenne primes, large semiprimes
   - ParallelPrimitives Blelloch scan correctness and tree reduction identity preservation
"""

import math
import random
import time
from collections.abc import Sequence

import pytest

from core.engine.approx.greedy_set_cover import CandidateSkillProfile, GreedySetCover
from core.engine.approx.knapsack_fptas import HiringCandidate, KnapsackFPTAS
from core.engine.approx.vertex_cover import VertexCoverApproximation
from core.engine.dp.bitmask_tsp import BitmaskTSP
from core.engine.dp.sequence_alignment import SequenceAlignment
from core.engine.dp.sos_dp import SkillDensityIndex, SOSDynamicProgramming
from core.engine.dp.tree_rerooting import TreeRerootingDP
from core.engine.dp.wagner_fischer import WagnerFischer
from core.engine.randomised.miller_rabin import MillerRabin
from core.engine.randomised.parallel_primitives import ParallelPrimitives
from core.engine.randomised.reservoir_sampling import ReservoirSampler

# ==============================================================================
# 1. DP: Wagner-Fischer Edit Distance Stress & Corner Cases
# ==============================================================================


def test_wagner_fischer_corner_cases():
    """Verify Wagner-Fischer behavior on boundary cases: empty strings, single char, disjoint."""
    # Empty vs Empty
    assert WagnerFischer.levenshtein_distance("", "") == 0
    assert WagnerFischer.damerau_levenshtein_distance("", "") == 0
    assert WagnerFischer.domain_weighted_distance("", "") == 0.0
    assert WagnerFischer.normalized_similarity("", "") == 1.0

    # One empty, one non-empty
    assert WagnerFischer.levenshtein_distance("python", "") == 6
    assert WagnerFischer.levenshtein_distance("", "python") == 6
    assert WagnerFischer.damerau_levenshtein_distance("python", "") == 6
    assert WagnerFischer.domain_weighted_distance("python", "", ins_cost=1.5, del_cost=2.0) == 12.0
    assert WagnerFischer.domain_weighted_distance("", "python", ins_cost=1.5, del_cost=2.0) == 9.0
    assert WagnerFischer.normalized_similarity("python", "") == 0.0
    assert WagnerFischer.normalized_similarity("", "python") == 0.0

    # Single char
    assert WagnerFischer.levenshtein_distance("a", "a") == 0
    assert WagnerFischer.levenshtein_distance("a", "b") == 1
    assert WagnerFischer.normalized_similarity("a", "a") == 1.0
    assert WagnerFischer.normalized_similarity("a", "b") == 0.0

    # Completely disjoint
    s1, s2 = "abcdef", "uvwxyz"
    assert WagnerFischer.levenshtein_distance(s1, s2) == 6
    assert WagnerFischer.damerau_levenshtein_distance(s1, s2) == 6
    assert WagnerFischer.normalized_similarity(s1, s2) == 0.0


def test_wagner_fischer_metric_properties():
    """Empirically test metric axioms: identity, symmetry, triangle inequality on random strings."""
    rng = random.Random(101)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    words = ["".join(rng.choices(alphabet, k=rng.randint(3, 8))) for _ in range(30)]

    for a in words:
        assert WagnerFischer.levenshtein_distance(a, a) == 0
        assert WagnerFischer.damerau_levenshtein_distance(a, a) == 0

    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            w1, w2 = words[i], words[j]
            # Symmetry
            assert WagnerFischer.levenshtein_distance(
                w1, w2
            ) == WagnerFischer.levenshtein_distance(w2, w1)
            assert WagnerFischer.damerau_levenshtein_distance(
                w1, w2
            ) == WagnerFischer.damerau_levenshtein_distance(w2, w1)

    # Triangle Inequality: d(a, c) <= d(a, b) + d(b, c)
    for _ in range(50):
        a, b, c = rng.sample(words, 3)
        d_ab = WagnerFischer.levenshtein_distance(a, b)
        d_bc = WagnerFischer.levenshtein_distance(b, c)
        d_ac = WagnerFischer.levenshtein_distance(a, c)
        assert d_ac <= d_ab + d_bc, (
            f"Triangle inequality violated: d({a},{c})={d_ac} > d({a},{b})={d_ab} + d({b},{c})={d_bc}"
        )


# ==============================================================================
# 2. DP: Sequence Alignment (Needleman-Wunsch & Smith-Waterman)
# ==============================================================================


def test_sequence_alignment_corner_cases():
    """Verify Needleman-Wunsch and Smith-Waterman on empty, single char, and disjoint strings."""
    sa = SequenceAlignment(match_score=2.0, mismatch_penalty=-1.0, gap_penalty=-1.0)

    # Empty vs Empty
    nw_empty = sa.needleman_wunsch("", "")
    assert nw_empty.score == 0.0
    assert nw_empty.aligned_seq1 == []
    assert nw_empty.aligned_seq2 == []
    assert nw_empty.identity_rate == 1.0

    sw_empty = sa.smith_waterman("", "")
    assert sw_empty.score == 0.0
    assert sw_empty.aligned_seq1 == []
    assert sw_empty.aligned_seq2 == []
    assert sw_empty.identity_rate == 0.0

    # One empty, one non-empty
    nw_one = sa.needleman_wunsch("abc", "")
    assert nw_one.score == -3.0
    assert nw_one.aligned_seq1 == ["a", "b", "c"]
    assert nw_one.aligned_seq2 == ["-", "-", "-"]
    assert nw_one.identity_rate == 0.0

    sw_one = sa.smith_waterman("abc", "")
    assert sw_one.score == 0.0
    assert sw_one.aligned_seq1 == []
    assert sw_one.aligned_seq2 == []

    # Single char identical vs different
    nw_same = sa.needleman_wunsch("X", "X")
    assert nw_same.score == 2.0
    assert nw_same.identity_rate == 1.0

    nw_diff = sa.needleman_wunsch("X", "Y")
    assert nw_diff.score == -1.0
    assert nw_diff.identity_rate == 0.0

    sw_same = sa.smith_waterman("X", "X")
    assert sw_same.score == 2.0
    assert sw_same.identity_rate == 1.0

    sw_diff = sa.smith_waterman("X", "Y")
    assert sw_diff.score == 0.0
    assert sw_diff.aligned_seq1 == []

    # Completely different strings
    nw_disjoint = sa.needleman_wunsch("AAAA", "BBBB")
    assert nw_disjoint.score == -4.0
    assert nw_disjoint.identity_rate == 0.0

    sw_disjoint = sa.smith_waterman("AAAA", "BBBB")
    assert sw_disjoint.score == 0.0
    assert sw_disjoint.aligned_seq1 == []


def test_smith_waterman_local_substring_extraction():
    """Verify that Smith-Waterman correctly identifies high-scoring local alignment surrounded by noise."""
    sa = SequenceAlignment(match_score=3.0, mismatch_penalty=-2.0, gap_penalty=-2.0)
    seq1 = "PREFIX_PYTHON_ENGINEER_SUFFIX"
    seq2 = "RANDOM_PYTHON_ENGINEER_GARBAGE"

    res = sa.smith_waterman(seq1, seq2)
    # Expected match is "_PYTHON_ENGINEER_" (17 characters * 3.0 = 51.0)
    extracted1 = "".join(res.aligned_seq1)
    extracted2 = "".join(res.aligned_seq2)
    assert extracted1 == "_PYTHON_ENGINEER_"
    assert extracted2 == "_PYTHON_ENGINEER_"
    assert res.score == 51.0
    assert res.identity_rate == 1.0


# ==============================================================================
# 3. DP: BitmaskTSP (n=12 Performance & Tour Reconstruction Defect)
# ==============================================================================


def test_bitmask_tsp_n12_performance():
    """Stress-test BitmaskTSP on n=12 cities to empirically verify execution completes in < 0.5s."""
    n = 12
    rng = random.Random(42)
    matrix = [[0.0 if i == j else float(rng.randint(5, 50)) for j in range(n)] for i in range(n)]

    t0 = time.perf_counter()
    cost, tour = BitmaskTSP.find_optimal_tour(matrix, start_node=0)
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.5, f"BitmaskTSP n=12 exceeded 0.5s threshold: {elapsed:.3f}s"
    assert cost > 0.0
    assert isinstance(tour, list)


def test_bitmask_tsp_tour_reconstruction_integrity():
    """Verify that BitmaskTSP.find_optimal_tour produces a valid Hamiltonian cycle without duplicated vertices.

    EXPECTED BUG: BitmaskTSP.find_optimal_tour initializes path=[start_node] AND appends start_node
    at the end, causing the tour to have length n+2 instead of n+1 with adjacent duplicates: [start, ..., start, start].
    """
    n = 4
    matrix = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0],
    ]
    cost, tour = BitmaskTSP.find_optimal_tour(matrix, start_node=0)

    # A valid TSP closed tour of n vertices must contain exactly n+1 vertices: [start, v1, v2, ..., start]
    assert len(tour) == n + 1, (
        f"DEFECT REPRODUCED: BitmaskTSP.find_optimal_tour returned tour of length {len(tour)} "
        f"for {n} cities: {tour}. Expected length {n + 1}."
    )
    assert tour[0] == 0 and tour[-1] == 0
    assert tour[-2] != tour[-1], (
        f"DEFECT REPRODUCED: BitmaskTSP.find_optimal_tour has duplicate adjacent end vertex: {tour}"
    )


def test_bitmask_tsp_open_path_integrity():
    """Verify that BitmaskTSP.find_optimal_path produces a valid Hamiltonian path of length n."""
    matrix = [
        [0, 5, 20],
        [5, 0, 7],
        [20, 7, 0],
    ]
    cost, path = BitmaskTSP.find_optimal_path(matrix, start_node=0)
    assert cost == 12.0
    assert len(path) == 3
    assert path == [0, 1, 2]


# ==============================================================================
# 4. DP: SOSDynamicProgramming (n=10 Mask Density vs Brute-Force Oracle)
# ==============================================================================


def test_sos_dp_n10_subsets_and_supersets_oracle():
    """Empirically verify Yates' SOS DP against a brute-force submask/superset oracle on n=10 bits (1024 masks)."""
    num_bits = 10
    size = 1 << num_bits
    rng = random.Random(777)
    values = [rng.randint(1, 50) for _ in range(size)]

    sos_sub = SOSDynamicProgramming.compute_subsets_sum(values, num_bits)
    sos_sup = SOSDynamicProgramming.compute_supersets_sum(values, num_bits)

    assert len(sos_sub) == size
    assert len(sos_sup) == size

    # Verify subset sum on all 1024 masks using submask enumeration: s = (s - 1) & m
    for m in range(size):
        oracle_sub = 0
        s = m
        while True:
            oracle_sub += values[s]
            if s == 0:
                break
            s = (s - 1) & m
        assert sos_sub[m] == oracle_sub, (
            f"Subset sum mismatch at mask {m}: SOS={sos_sub[m]}, Oracle={oracle_sub}"
        )

    # Verify superset sum on a sample of masks
    sample_masks = [0, 1, 7, 15, 31, 63, 127, 255, 511, 1023, 42, 137, 729]
    for m in sample_masks:
        oracle_sup = sum(values[s] for s in range(size) if (s & m) == m)
        assert sos_sup[m] == oracle_sup, (
            f"Superset sum mismatch at mask {m}: SOS={sos_sup[m]}, Oracle={oracle_sup}"
        )


def test_skill_density_index_queries():
    """Verify SkillDensityIndex correctness with 500 candidates across 10 skills."""
    num_skills = 10
    rng = random.Random(888)
    cand_masks = [rng.randint(0, (1 << num_skills) - 1) for _ in range(500)]

    index = SkillDensityIndex(num_skills=num_skills)
    for m in cand_masks:
        index.add_candidate_mask(m)
    index.build_index()

    test_queries = [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 42, 137]
    for req in test_queries:
        # All skills required: candidate must possess at least all bits in req
        expected_all = sum(1 for m in cand_masks if (m & req) == req)
        assert index.count_candidates_with_all_skills(req) == expected_all

        # Subset of skills: candidate's skills must be a subset of allowable
        expected_sub = sum(1 for m in cand_masks if (m & ~req) == 0)
        assert index.count_candidates_with_subset_of_skills(req) == expected_sub


# ==============================================================================
# 5. DP: TreeRerootingDP (Path, Star, Balanced Binary Tree, Weighted Headcounts)
# ==============================================================================


def _bfs_all_distances_oracle(
    adj: list[list[int]], headcounts: list[int] | None = None
) -> list[float]:
    """Independent BFS oracle to compute all-nodes distance sum."""
    n = len(adj)
    weights = headcounts if headcounts else [1] * n
    res = [0.0] * n
    for start in range(n):
        dist = [-1] * n
        dist[start] = 0
        q = [start]
        head = 0
        while head < len(q):
            u = q[head]
            head += 1
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        res[start] = float(sum(dist[v] * weights[v] for v in range(n)))
    return res


def test_tree_rerooting_path_graph():
    """Verify TreeRerootingDP on path graph N=20 against closed-form and BFS oracle."""
    n = 20
    adj = [[] for _ in range(n)]
    for i in range(n - 1):
        adj[i].append(i + 1)
        adj[i + 1].append(i)

    actual = TreeRerootingDP.compute_all_distances(adj)
    oracle = _bfs_all_distances_oracle(adj)
    assert actual == oracle

    # In path graph of length 20, centroid is 9 or 10
    centroid = TreeRerootingDP.find_centroid(adj)
    assert centroid in (9, 10)


def test_tree_rerooting_star_graph():
    """Verify TreeRerootingDP on star graph N=30: center must have min latency and be centroid."""
    n = 30
    adj = [[] for _ in range(n)]
    for i in range(1, n):
        adj[0].append(i)
        adj[i].append(0)

    actual = TreeRerootingDP.compute_all_distances(adj)
    oracle = _bfs_all_distances_oracle(adj)
    assert actual == oracle

    # Center (0) distance is n-1 = 29; leaves distance is 1 + 2*(n-2) = 57
    assert actual[0] == 29.0
    for leaf in range(1, n):
        assert actual[leaf] == 57.0

    assert TreeRerootingDP.find_centroid(adj) == 0


def test_tree_rerooting_balanced_tree_and_weights():
    """Verify TreeRerootingDP on balanced binary tree N=31 with non-uniform headcounts."""
    n = 31
    adj = [[] for _ in range(n)]
    for i in range(n):
        left, right = 2 * i + 1, 2 * i + 2
        if left < n:
            adj[i].append(left)
            adj[left].append(i)
        if right < n:
            adj[i].append(right)
            adj[right].append(i)

    rng = random.Random(999)
    headcounts = [rng.randint(1, 100) for _ in range(n)]

    actual = TreeRerootingDP.compute_all_distances(adj, headcounts=headcounts)
    oracle = _bfs_all_distances_oracle(adj, headcounts=headcounts)
    for u in range(n):
        assert abs(actual[u] - oracle[u]) < 1e-6

    report = TreeRerootingDP.balance_headcounts(adj, headcounts)
    assert report.min_total_latency == min(actual)
    assert report.total_headcount == sum(headcounts)


# ==============================================================================
# 6. Approx: GreedySetCover (1 + ln n) Approximation Ratio Verification
# ==============================================================================


def _exact_set_cover_oracle(
    candidates: Sequence[CandidateSkillProfile], target_skills: set[str]
) -> float:
    """Exact minimum cost set cover oracle using branch-and-bound."""
    U = sorted(list(target_skills))
    skill_to_bit = {s: 1 << i for i, s in enumerate(U)}
    target_mask = (1 << len(U)) - 1

    cand_masks = []
    for c in candidates:
        m = 0
        for s in c.skills:
            if s in skill_to_bit:
                m |= skill_to_bit[s]
        cand_masks.append((m, c.cost))

    best_cost = [float("inf")]

    def search(idx: int, cur_mask: int, cur_cost: float) -> None:
        if cur_cost >= best_cost[0]:
            return
        if cur_mask == target_mask:
            best_cost[0] = cur_cost
            return
        if idx == len(cand_masks):
            return
        # Branch take
        search(idx + 1, cur_mask | cand_masks[idx][0], cur_cost + cand_masks[idx][1])
        # Branch skip
        search(idx + 1, cur_mask, cur_cost)

    search(0, 0, 0.0)
    return best_cost[0]


def test_greedy_set_cover_approximation_bound():
    """Verify GreedySetCover approximation ratio <= (1 + ln |U|) * OPT across 50 random instances."""
    rng = random.Random(1234)
    all_skills = [f"skill_{i}" for i in range(12)]

    for trial in range(50):
        k = rng.randint(4, 8)
        targets = set(rng.sample(all_skills, k))
        num_cands = rng.randint(5, 10)
        cands = []
        for cid in range(num_cands):
            c_skills = rng.sample(list(targets), rng.randint(1, min(len(targets), 4)))
            cost = rng.uniform(1.0, 15.0)
            cands.append(CandidateSkillProfile(f"cand_{cid}", c_skills, cost))

        opt_cost = _exact_set_cover_oracle(cands, targets)
        if opt_cost == float("inf"):
            continue

        result = GreedySetCover.find_minimum_team(cands, targets)
        assert len(result.uncovered_skills) == 0

        # Theoretical guarantee: Cost(Greedy) <= (1 + ln |U|) * OPT
        bound = (1.0 + math.log(len(targets))) * opt_cost + 1e-6
        assert result.total_cost <= bound, (
            f"Set cover approximation bound violated in trial {trial}: "
            f"Cost={result.total_cost:.3f} > Bound={bound:.3f} (OPT={opt_cost:.3f})"
        )


def test_greedy_set_cover_corner_cases():
    """Test GreedySetCover with empty target skills and uncoverable skills."""
    cands = [
        CandidateSkillProfile("c1", ["python", "sql"], cost=10.0),
        CandidateSkillProfile("c2", ["react"], cost=5.0),
    ]
    # Empty targets
    res_empty = GreedySetCover.find_minimum_team(cands, [])
    assert res_empty.total_cost == 0.0
    assert res_empty.selected_candidates == []

    # Uncoverable skills
    res_uncoverable = GreedySetCover.find_minimum_team(cands, ["python", "kubernetes"])
    assert "kubernetes" in res_uncoverable.uncovered_skills
    assert "python" in res_uncoverable.covered_skills


# ==============================================================================
# 7. Approx: VertexCover 2-Approximation Verification
# ==============================================================================


def _exact_vertex_cover_oracle(num_vertices: int, edges: list[tuple[int, int]]) -> int:
    """Exact minimum vertex cover oracle using bitmask enumeration."""
    import itertools

    for size in range(num_vertices + 1):
        for cover in itertools.combinations(range(num_vertices), size):
            cover_set = set(cover)
            if all(u in cover_set or v in cover_set for u, v in edges):
                return size
    return num_vertices


def test_vertex_cover_2_approximation_bound():
    """Empirically verify VertexCoverApproximation produces valid cover with size <= 2 * OPT."""
    rng = random.Random(4321)

    for trial in range(50):
        n = rng.randint(4, 12)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.35:
                    edges.append((u, v))
        if not edges:
            continue

        opt = _exact_vertex_cover_oracle(n, edges)
        cover = VertexCoverApproximation.approximate_vertex_cover(n, edges)

        # 1. Validity check: Every edge must be covered
        cov_set = set(cover)
        for u, v in edges:
            assert u in cov_set or v in cov_set, f"Edge ({u}, {v}) not covered by {cov_set}"

        # 2. 2-approximation check: size <= 2 * OPT
        assert len(cover) <= 2 * opt, (
            f"2-approximation violated: Cover size {len(cover)} > 2 * OPT {2 * opt}"
        )


# ==============================================================================
# 8. Approx: KnapsackFPTAS (1 - epsilon) Bound Verification
# ==============================================================================


def _exact_knapsack_oracle(candidates: Sequence[HiringCandidate], budget: float) -> float:
    """Exact 0-1 knapsack branch-and-bound oracle."""
    n = len(candidates)
    best_val = [0.0]
    cand = sorted(candidates, key=lambda c: c.value / c.cost if c.cost > 0 else 1e9, reverse=True)

    def search(i: int, cur_cost: float, cur_val: float) -> None:
        if cur_cost > budget:
            return
        best_val[0] = max(best_val[0], cur_val)
        if i == n:
            return
        rem_budget = budget - cur_cost
        bound = cur_val
        for j in range(i, n):
            if cand[j].cost <= rem_budget:
                bound += cand[j].value
                rem_budget -= cand[j].cost
            else:
                bound += cand[j].value * (rem_budget / cand[j].cost)
                break
        if bound <= best_val[0]:
            return
        search(i + 1, cur_cost + cand[i].cost, cur_val + cand[i].value)
        search(i + 1, cur_cost, cur_val)

    search(0, 0.0, 0.0)
    return best_val[0]


def test_knapsack_fptas_epsilon_bound():
    """Verify KnapsackFPTAS satisfies total_value >= (1 - epsilon) * OPT on 50 instances."""
    rng = random.Random(555)

    for trial in range(50):
        n = rng.randint(4, 12)
        budget = rng.uniform(30.0, 80.0)
        cands = [
            HiringCandidate(i, rng.uniform(5.0, 30.0), rng.uniform(10.0, 60.0)) for i in range(n)
        ]

        opt = _exact_knapsack_oracle(cands, budget)
        if opt == 0:
            continue

        for eps in [0.5, 0.2, 0.1]:
            res = KnapsackFPTAS.solve(cands, budget, epsilon=eps)
            assert res.total_cost <= budget + 1e-6, f"Budget exceeded: {res.total_cost} > {budget}"
            ratio = res.total_value / opt
            assert ratio >= (1.0 - eps - 1e-6), (
                f"FPTAS (1-eps) bound violated: trial {trial}, eps={eps}, ratio={ratio:.4f} < {1.0 - eps}"
            )


# ==============================================================================
# 9. Randomised: ReservoirSampler Uniformity Chi-Square Test
# ==============================================================================


def test_reservoir_sampler_uniformity_chi_square():
    """Empirically test ReservoirSampler uniformity via Pearson Chi-Square goodness-of-fit test.

    N = 20, k = 5, M = 20,000 trials.
    Under uniform sampling, expected frequency E_i = 5000.
    Degrees of freedom = 19.
    Critical value for alpha = 0.01 is 36.19.
    """
    N = 20
    k = 5
    M = 20000
    stream = list(range(N))

    counts = [0] * N
    for _ in range(M):
        sample = ReservoirSampler.sample_stream(stream, k, seed=None)
        assert len(sample) == k
        for item in sample:
            counts[item] += 1

    expected = M * (k / N)
    chi2 = sum((obs - expected) ** 2 / expected for obs in counts)

    # Chi-square critical value for df=19 at alpha=0.01 is 36.19
    assert chi2 < 36.19, (
        f"ReservoirSampler failed Chi-Square uniformity test: chi2={chi2:.2f} >= 36.19 (df=19, alpha=0.01). "
        f"Counts: {counts}"
    )


def test_reservoir_sampler_boundary_conditions():
    """Verify ReservoirSampler when stream length <= k or empty."""
    # N < k
    sample_small = ReservoirSampler.sample_stream([1, 2, 3], k=5)
    assert sorted(sample_small) == [1, 2, 3]

    # N == k
    sample_exact = ReservoirSampler.sample_stream([10, 20, 30], k=3)
    assert sorted(sample_exact) == [10, 20, 30]

    # Empty stream
    sample_empty = ReservoirSampler.sample_stream([], k=5)
    assert sample_empty == []

    # Invalid k
    with pytest.raises(ValueError):
        ReservoirSampler(k=0)
    with pytest.raises(ValueError):
        ReservoirSampler(k=-1)


# ==============================================================================
# 10. Randomised: Miller-Rabin Primality Verification
# ==============================================================================


def test_miller_rabin_sieve_verification():
    """Verify MillerRabin.is_prime on all integers up to 5,000 against a prime sieve oracle."""
    limit = 5000
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            for i in range(p * p, limit + 1, p):
                sieve[i] = False

    for n in range(limit + 1):
        assert MillerRabin.is_prime(n) == sieve[n], f"Primality mismatch at n={n}"


def test_miller_rabin_carmichael_numbers():
    """Verify that Miller-Rabin correctly identifies Carmichael pseudoprimes as composite."""
    carmichael_numbers = [
        561,
        1105,
        1729,
        2465,
        2821,
        6601,
        8911,
        41041,
        62745,
        63973,
        75361,
        101101,
        115921,
        126217,
        162401,
        172081,
    ]
    for c in carmichael_numbers:
        assert not MillerRabin.is_prime(c), f"Carmichael number {c} falsely classified as prime"


def test_miller_rabin_mersenne_primes_and_semiprimes():
    """Verify Miller-Rabin on Mersenne primes up to 2^127 - 1 and large semiprimes."""
    mersenne_powers = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127]
    for p in mersenne_powers:
        val = (1 << p) - 1
        assert MillerRabin.is_prime(val), f"Mersenne prime 2^{p} - 1 classified as composite"

    # Large semiprimes
    p1 = 1000000007
    p2 = 1000000009
    assert not MillerRabin.is_prime(p1 * p2)
    assert not MillerRabin.is_prime(p1 * p1)


# ==============================================================================
# 11. Randomised: ParallelPrimitives Prefix-Sum & Tree-Reduction
# ==============================================================================


def test_parallel_primitives_blelloch_scan_correctness():
    """Verify Blelloch work-efficient parallel scan against serial prefix sum on various lengths."""
    test_cases = [
        [],
        [42],
        [10, 20],
        [3, 1, 7],
        [1, 2, 3, 4, 5, 6, 7, 8],
        [-3, 5, -2, 4, 10, -8, 0, 7],
        list(range(1, 100)),
    ]

    for data in test_cases:
        res = ParallelPrimitives.blelloch_scan(data)
        n = len(data)
        if n == 0:
            assert res.exclusive_scan == []
            assert res.inclusive_scan == []
            continue

        # Serial exclusive prefix sum
        expected_exclusive = [0] * n
        for i in range(1, n):
            expected_exclusive[i] = expected_exclusive[i - 1] + data[i - 1]

        # Serial inclusive prefix sum
        expected_inclusive = [0] * n
        expected_inclusive[0] = data[0]
        for i in range(1, n):
            expected_inclusive[i] = expected_inclusive[i - 1] + data[i]

        assert res.exclusive_scan == expected_exclusive, (
            f"Exclusive scan mismatch on data={data[:10]}"
        )
        assert res.inclusive_scan == expected_inclusive, (
            f"Inclusive scan mismatch on data={data[:10]}"
        )

        # Work-span properties
        m = ParallelPrimitives._next_power_of_two(n)
        assert res.metrics.work == 3 * (m - 1)
        assert res.metrics.span == 2 * int(math.log2(m)) if m > 1 else res.metrics.span == 0


def test_parallel_primitives_tree_reduce_non_zero_identity():
    """Verify tree_reduce behavior on non-power-of-2 arrays with operators whose identity != 0.

    EXPECTED BUG: ParallelPrimitives.tree_reduce pads the array with 0 (line 137).
    When reducing with op=max on an all-negative array (e.g. [-10, -20, -30]),
    the 0 padding corrupts the reduction and returns 0 instead of -10!
    Similarly with op=min on positive arrays ([10, 20, 30]), returns 0 instead of 10.
    """
    # Sum works because 0 is the additive identity
    res_sum = ParallelPrimitives.tree_reduce([1, 2, 3, 4, 5])
    assert res_sum.value == 15

    # Max on negative numbers: length 3 is not a power of 2
    res_max = ParallelPrimitives.tree_reduce([-10, -20, -30], op=max)
    assert res_max.value == -10, (
        f"DEFECT REPRODUCED: ParallelPrimitives.tree_reduce returned {res_max.value} instead of -10. "
        f"Buffer was padded with 0, which is not the identity for max."
    )

    # Min on positive numbers: length 3 is not a power of 2
    res_min = ParallelPrimitives.tree_reduce([10, 20, 30], op=min)
    assert res_min.value == 10, (
        f"DEFECT REPRODUCED: ParallelPrimitives.tree_reduce returned {res_min.value} instead of 10. "
        f"Buffer was padded with 0, which is not the identity for min."
    )
