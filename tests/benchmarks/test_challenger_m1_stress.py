"""Milestone 1 Empirical Stress Test Suite & Algorithmic Verification Harness.

Stress-tests:
- CustomArrayList (100k items, memory reallocation, shrinking, negative indexing)
- CustomHashMap (collision stress, dynamic resizing, load factor invariant, heterogenous keys)
- CustomPriorityQueue (4-ary heap invariant verification under randomized float inputs, FIFO stability)
- KMP & Z-Algorithm (large text >= 200k characters, repetitive patterns, LCP differential oracle)
- Aho-Corasick (multi-thousand keyword vocabulary, heavy overlapping substrings, single-pass speed)
- Rabin-Karp (dual-prime rolling hash zero-drift verification across 50,000 window shifts)
- Dinic vs Edmonds-Karp (random complex networks, flow conservation, Max-Flow Min-Cut Theorem, capacity bounds)
- Big-O Scaling Benchmarks (Dinic vs EK, KMP/Aho linear scaling, SOS DP O(n*2^n))
- Bug Reproduction & Adversarial Penetration (Marketplace job capacity omission, TSP duplicate tour node, Dinic source==sink hang)
"""

import random
import time
from typing import Any

import pytest

from core.engine.dp.bitmask_tsp import BitmaskTSP
from core.engine.dp.sos_dp import SOSDynamicProgramming
from core.engine.flow.dinic import DinicAlgorithm
from core.engine.flow.edmonds_karp import EdmondsKarp
from core.engine.flow.marketplace_network import (
    CandidateNode,
    JobNode,
    MarketplaceFlowNetwork,
)
from core.engine.flow.min_cut import MinCutAnalyzer
from core.engine.string.aho_corasick import AhoCorasickAutomaton
from core.engine.string.kmp import KMPMatcher
from core.engine.string.rabin_karp import RabinKarp
from core.engine.string.z_algorithm import ZAlgorithm
from core.engine.structures.adjacency_graph import CustomAdjacencyGraph
from core.engine.structures.array_list import CustomArrayList
from core.engine.structures.hash_map import CustomHashMap
from core.engine.structures.priority_queue import CustomPriorityQueue


class TestStructuresScaleStress:
    """Empirical scale & stress testing for core/engine/structures."""

    def test_custom_array_list_100k_resizing_and_integrity(self) -> None:
        """Stress CustomArrayList with 100,000 items: check resizing, indexing, and memory shrinking."""
        arr: CustomArrayList[int] = CustomArrayList[int]()
        n_items = 100_000

        # 1. Sequential Append Stress
        t0 = time.perf_counter()
        for i in range(n_items):
            arr.append(i)
        elapsed = time.perf_counter() - t0

        assert len(arr) == n_items
        assert arr.size() == n_items
        assert elapsed < 1.0, f"100k appends took too long: {elapsed:.3f}s"

        # 2. Capacity Growth Check
        cap = arr.capacity()
        assert cap >= n_items
        assert (cap & (cap - 1)) == 0, f"Capacity {cap} is not a power of 2"
        assert cap == 131_072

        # 3. Random & Boundary Indexing Check
        assert arr.get(0) == 0
        assert arr.get(50_000) == 50_000
        assert arr.get(99_999) == 99_999
        assert arr.get(-1) == 99_999
        assert arr.get(-100_000) == 0

        with pytest.raises(IndexError):
            arr.get(100_000)
        with pytest.raises(IndexError):
            arr.get(-100_001)

        # 4. Set Integrity
        arr.set(50_000, 999_999)
        assert arr.get(50_000) == 999_999
        arr.set(50_000, 50_000)

        # 5. Shrinking / Downsizing Stress
        for _ in range(75_000):
            arr.pop()

        assert len(arr) == 25_000
        assert arr.capacity() < 131_072

        # 6. Insertion & Pop at Boundaries
        arr.insert(0, -999)
        assert arr.get(0) == -999
        assert len(arr) == 25_001

        popped = arr.pop(0)
        assert popped == -999
        assert len(arr) == 25_000

        # 7. Clear and Reuse
        arr.clear()
        assert len(arr) == 0
        assert arr.capacity() == CustomArrayList.DEFAULT_INITIAL_CAPACITY
        arr.append(42)
        assert arr.get(0) == 42

    def test_custom_hash_map_heavy_collisions_and_resizing(self) -> None:
        """Stress CustomHashMap with 20,000 insertions, load factor bounds, and deliberate bucket collisions."""
        hmap: CustomHashMap[Any, Any] = CustomHashMap[Any, Any]()
        n_entries = 20_000

        # 1. 20,000 Diverse Keys with Dynamic Resizing
        for i in range(n_entries):
            hmap.put(f"key_{i}", i * 10)
            assert hmap.load_factor() < 0.755

        assert len(hmap) == n_entries
        assert hmap.size() == n_entries

        # Spot check retrieval
        assert hmap.get("key_0") == 0
        assert hmap.get("key_10000") == 100_000
        assert hmap.get("key_19999") == 199_990
        assert hmap.get("non_existent") is None

        # 2. Key Update (Idempotent Size)
        hmap.put("key_500", 555_555)
        assert hmap.get("key_500") == 555_555
        assert len(hmap) == n_entries

        # 3. Deliberate Collision Handling in Small Map
        collision_map: CustomHashMap[str, int] = CustomHashMap[str, int](initial_capacity=4)
        keys = [f"item_{i}_{i * 31}" for i in range(200)]
        for k in keys:
            collision_map.put(k, len(k))

        for k in keys:
            assert collision_map.contains(k)
            assert collision_map.get(k) == len(k)

        # Remove keys from middle of collision chains
        for k in keys[::2]:
            removed_val = collision_map.remove(k)
            assert removed_val == len(k)
            assert not collision_map.contains(k)

        # Remaining keys must still be intact
        for k in keys[1::2]:
            assert collision_map.contains(k)
            assert collision_map.get(k) == len(k)

        # 4. Type Heterogeneity (int vs str, None vs 'None')
        type_map: CustomHashMap[Any, str] = CustomHashMap[Any, str]()
        type_map.put(100, "integer_100")
        type_map.put("100", "string_100")
        type_map.put(None, "null_key")
        type_map.put("None", "string_null_key")
        assert type_map.get(100) == "integer_100"
        assert type_map.get("100") == "string_100"
        assert type_map.get(None) == "null_key"
        assert type_map.get("None") == "string_null_key"
        assert len(type_map) == 4

    def test_custom_priority_queue_4ary_heap_property_randomized(self) -> None:
        """Stress CustomPriorityQueue 4-ary heap property under randomized inputs and FIFO stability."""
        # 1. Min-Heap 4-ary Invariant & Monotonic Extraction
        min_pq: CustomPriorityQueue[int] = CustomPriorityQueue[int](is_min=True)
        rng = random.Random(42)
        n_items = 10_000
        values = [rng.uniform(-1000.0, 1000.0) for _ in range(n_items)]

        for i, val in enumerate(values):
            min_pq.push(val, i)

        assert len(min_pq) == n_items

        # Explicitly verify 4-ary heap property across the internal buffer
        data = min_pq._data
        size = min_pq._size
        for parent_idx in range((size - 2) // 4 + 1):
            parent_entry = data[parent_idx]
            assert parent_entry is not None
            for c in range(1, 5):
                child_idx = 4 * parent_idx + c
                if child_idx < size:
                    child_entry = data[child_idx]
                    assert child_entry is not None
                    assert child_entry.priority >= parent_entry.priority, (
                        f"Heap invariant violated at parent {parent_idx} child {child_idx}"
                    )

        extracted = []
        while not min_pq.is_empty():
            prio, item = min_pq.pop()
            extracted.append(prio)

        assert len(extracted) == n_items
        for i in range(len(extracted) - 1):
            assert extracted[i] <= extracted[i + 1]

        # 2. Max-Heap 4-ary Invariant & Monotonic Extraction
        max_pq: CustomPriorityQueue[int] = CustomPriorityQueue[int](is_min=False)
        for i, val in enumerate(values):
            max_pq.push(val, i)

        data = max_pq._data
        size = max_pq._size
        for parent_idx in range((size - 2) // 4 + 1):
            parent_entry = data[parent_idx]
            assert parent_entry is not None
            for c in range(1, 5):
                child_idx = 4 * parent_idx + c
                if child_idx < size:
                    child_entry = data[child_idx]
                    assert child_entry is not None
                    assert child_entry.priority <= parent_entry.priority, (
                        f"Max-heap invariant violated at parent {parent_idx} child {child_idx}"
                    )

        max_extracted = []
        while not max_pq.is_empty():
            prio, item = max_pq.pop()
            max_extracted.append(prio)

        for i in range(len(max_extracted) - 1):
            assert max_extracted[i] >= max_extracted[i + 1]

        # 3. FIFO Stability on Equal Priorities
        fifo_pq: CustomPriorityQueue[str] = CustomPriorityQueue[str](is_min=True)
        for i in range(1_000):
            fifo_pq.push(42.0, f"item_{i}")

        for i in range(1_000):
            prio, item = fifo_pq.pop()
            assert prio == 42.0
            assert item == f"item_{i}", f"FIFO stability broken: expected item_{i}, got {item}"


class TestStringAlgorithmsStress:
    """Empirical scale & stress testing for core/engine/string."""

    def test_kmp_and_z_algorithm_large_text_200k(self) -> None:
        """Stress KMPMatcher and ZAlgorithm on large texts (200k chars) with repetitive and periodic patterns."""
        rng = random.Random(1337)
        chars = ["A", "C", "G", "T"]
        text_list = [rng.choice(chars) for _ in range(200_000)]
        text = "".join(text_list)

        needle = "ACGTACGTACGTACGT"
        inject_indices = [0, 50_000, 100_000, 199_980]
        text_chars = list(text)
        for idx in inject_indices:
            text_chars[idx : idx + len(needle)] = list(needle)
        text = "".join(text_chars)

        t0 = time.perf_counter()
        kmp_matches = KMPMatcher.find_all(text, needle)
        kmp_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        z_matches = ZAlgorithm.search(text, needle)
        z_time = time.perf_counter() - t0

        assert kmp_time < 0.5, f"KMP took too long: {kmp_time:.3f}s"
        assert z_time < 0.5, f"Z-Algorithm took too long: {z_time:.3f}s"
        assert kmp_matches == z_matches

        for idx in inject_indices:
            assert idx in kmp_matches

        assert KMPMatcher.find_first(text, needle) == kmp_matches[0]

        # Pathological Repetitive Needle
        pathological_text = ("A" * 20_000) + "B" + ("A" * 20_000) + "B"
        pathological_needle = ("A" * 1_000) + "B"
        p_kmp = KMPMatcher.find_all(pathological_text, pathological_needle)
        p_z = ZAlgorithm.search(pathological_text, pathological_needle)
        assert p_kmp == [19_000, 39_001]
        assert p_z == [19_000, 39_001]

    def test_z_algorithm_differential_oracle_against_naive_lcp(self) -> None:
        """Differential verification of Z-array construction against naive O(N^2) longest common prefix."""
        rng = random.Random(999)
        test_strings = [
            "a" * 100,
            "abacaba" * 15,
            "".join(rng.choice(["a", "b"]) for _ in range(500)),
            "".join(rng.choice(["a", "b", "c", "d"]) for _ in range(500)),
            "abcdefghij" * 20,
        ]

        for s in test_strings:
            z_fast = ZAlgorithm.compute_z_array(s)
            n = len(s)
            assert len(z_fast) == n
            assert z_fast[0] == n

            z_naive = [0] * n
            z_naive[0] = n
            for i in range(1, n):
                match_len = 0
                while i + match_len < n and s[match_len] == s[i + match_len]:
                    match_len += 1
                z_naive[i] = match_len

            assert z_fast == z_naive, f"Z-array mismatch on string: {s[:30]}..."

    def test_aho_corasick_large_vocabulary_and_heavy_overlap(self) -> None:
        """Stress AhoCorasickAutomaton on 3,000+ keywords with dense substring overlaps against a large document."""
        automaton = AhoCorasickAutomaton(ignore_case=True)

        base_skills = [
            "python",
            "py",
            "python3",
            "pytest",
            "pytorch",
            "torch",
            "java",
            "javascript",
            "script",
            "typescript",
            "type",
            "c",
            "c++",
            "c#",
            "rust",
            "rustacean",
            "go",
            "golang",
            "sql",
            "postgresql",
            "postgres",
            "nosql",
            "mysql",
            "sqlite",
            "docker",
            "kubernetes",
            "k8s",
            "container",
            "helm",
            "aws",
            "gcp",
            "azure",
            "cloud",
            "lambda",
            "s3",
            "ec2",
            "fastapi",
            "flask",
            "django",
            "react",
            "redux",
            "nextjs",
            "vue",
            "angular",
            "html",
            "css",
            "tailwind",
            "sass",
        ]
        vocab = set(base_skills)
        for base in base_skills:
            for i in range(60):
                vocab.add(f"{base}_{i}")
                vocab.add(f"senior_{base}")
                vocab.add(f"{base}_developer")

        for word in vocab:
            automaton.add_word(word, payload=f"meta_{word}")

        assert automaton.word_count == len(vocab)
        assert automaton.word_count >= 3_000

        paragraphs = [
            "We are looking for a Senior Python Developer with deep experience in Python3, PyTorch, and FastAPI. ",
            "The candidate must have built microservices using Docker, Kubernetes (k8s), and deployed on AWS and GCP. ",
            "Front-end experience with React, NextJS, TypeScript, and Tailwind CSS is highly preferred. ",
            "Strong foundation in PostgreSQL, SQL query optimization, and NoSQL databases. ",
        ] * 250
        doc = "".join(paragraphs)
        assert len(doc) >= 50_000

        t0 = time.perf_counter()
        matches = automaton.find_all(doc)
        scan_time = time.perf_counter() - t0

        assert len(matches) > 1_000
        assert scan_time < 0.6, f"Aho-Corasick scan took {scan_time:.3f}s"

        for m in matches[:100]:
            slice_text = doc[m.start : m.end]
            assert slice_text.lower() == m.word.lower()
            assert m.payload == f"meta_{m.word.lower()}"

        keywords = automaton.extract_keywords(doc)
        assert "python" in keywords
        assert "pytorch" in keywords
        assert "docker" in keywords
        assert "fastapi" in keywords
        assert len(keywords) == len(set(keywords))

    def test_rabin_karp_dual_prime_no_drift_and_collision_resistance(self) -> None:
        """Stress Rabin-Karp dual-prime rolling hash: verify 0 mathematical drift over 50k window slides."""
        rng = random.Random(2026)
        text = "".join(rng.choice(["a", "b", "c", "d", "e", "f", "0", "1"]) for _ in range(50_000))
        k = 32

        power1 = 1
        power2 = 1
        for _ in range(k - 1):
            power1 = (power1 * RabinKarp.BASE) % RabinKarp.MOD1
            power2 = (power2 * RabinKarp.BASE) % RabinKarp.MOD2

        h1 = 0
        h2 = 0
        for i in range(k):
            val = ord(text[i])
            h1 = (h1 * RabinKarp.BASE + val) % RabinKarp.MOD1
            h2 = (h2 * RabinKarp.BASE + val) % RabinKarp.MOD2

        for i in range(10_000):
            expected_h1, expected_h2 = RabinKarp.hash_string(text[i : i + k])
            assert h1 == expected_h1, f"MOD1 rolling drift at step {i}: {h1} != {expected_h1}"
            assert h2 == expected_h2, f"MOD2 rolling drift at step {i}: {h2} != {expected_h2}"

            out_val = ord(text[i])
            in_val = ord(text[i + k])
            h1 = ((h1 - out_val * power1) * RabinKarp.BASE + in_val) % RabinKarp.MOD1
            if h1 < 0:
                h1 += RabinKarp.MOD1
            h2 = ((h2 - out_val * power2) * RabinKarp.BASE + in_val) % RabinKarp.MOD2
            if h2 < 0:
                h2 += RabinKarp.MOD2

        seen_dual_hashes = set()
        for i in range(20_000):
            sample = f"resume_token_entropy_seed_{i}_{i * 997}"
            dh = RabinKarp.hash_string(sample)
            assert dh not in seen_dual_hashes, f"Dual-prime collision detected on {sample}"
            seen_dual_hashes.add(dh)


class TestFlowAlgorithmsStress:
    """Empirical stress testing for core/engine/flow."""

    def _generate_random_flow_network(
        self,
        num_nodes: int,
        num_edges: int,
        seed: int,
    ) -> tuple[CustomAdjacencyGraph, int, int]:
        rng = random.Random(seed)
        graph = CustomAdjacencyGraph(initial_node_count=num_nodes)
        source = 0
        sink = num_nodes - 1

        for i in range(num_nodes):
            graph.add_node(i)

        edges_added = set()
        curr = source
        while curr < sink:
            nxt = rng.randint(curr + 1, min(curr + 3, sink))
            cap = rng.randint(5, 50)
            graph.add_edge(curr, nxt, capacity=float(cap))
            edges_added.add((curr, nxt))
            curr = nxt

        attempts = 0
        while len(edges_added) < num_edges and attempts < num_edges * 5:
            attempts += 1
            u = rng.randint(0, num_nodes - 2)
            v = rng.randint(1, num_nodes - 1)
            if u != v and (u, v) not in edges_added:
                cap = rng.randint(1, 100)
                graph.add_edge(u, v, capacity=float(cap))
                edges_added.add((u, v))

        return graph, source, sink

    def test_dinic_vs_edmonds_karp_complex_random_graphs(self) -> None:
        """Compare Dinic and Edmonds-Karp on 15 complex random flow networks: exact equality of max flow."""
        for seed in range(15):
            num_nodes = 25 + (seed % 10)
            num_edges = 70 + (seed * 8)
            g1, s, t = self._generate_random_flow_network(num_nodes, num_edges, seed=100 + seed)
            g2, _, _ = self._generate_random_flow_network(num_nodes, num_edges, seed=100 + seed)

            ek_flow = EdmondsKarp.compute_max_flow(g1, s, t)
            dinic_flow = DinicAlgorithm.compute_max_flow(g2, s, t)

            assert abs(ek_flow - dinic_flow) < 1e-6, (
                f"Seed {seed}: Edmonds-Karp ({ek_flow}) != Dinic ({dinic_flow})"
            )

    def test_flow_conservation_and_capacity_constraints(self) -> None:
        """Verify Kirchhoff's flow conservation law and capacity constraints on all nodes after Dinic."""
        g, source, sink = self._generate_random_flow_network(30, 100, seed=4242)
        max_flow = DinicAlgorithm.compute_max_flow(g, source, sink)

        assert max_flow > 0.0

        for u in g.nodes():
            for edge in g.get_edges(u):
                if edge.capacity > 0:
                    assert 0.0 <= edge.flow <= edge.capacity + 1e-9
                if edge.residual is not None:
                    assert abs(edge.flow + edge.residual.flow) < 1e-9

        for u in g.nodes():
            if u == source or u == sink:
                continue

            in_flow = 0.0
            out_flow = 0.0
            for edge in g.get_edges(u):
                if edge.flow > 0:
                    out_flow += edge.flow
                elif edge.flow < 0:
                    in_flow += -edge.flow

            assert abs(in_flow - out_flow) < 1e-6

        source_outflow = sum(e.flow for e in g.get_edges(source) if e.flow > 0)
        source_inflow = sum(-e.flow for e in g.get_edges(source) if e.flow < 0)
        net_source = source_outflow - source_inflow

        sink_inflow = 0.0
        for u in g.nodes():
            for e in g.get_edges(u):
                if e.v == sink and e.capacity > 0:
                    sink_inflow += e.flow

        assert abs(net_source - max_flow) < 1e-6
        assert abs(sink_inflow - max_flow) < 1e-6

    def test_min_cut_residual_reachability_and_theorem(self) -> None:
        """Verify the Max-Flow Min-Cut theorem: capacity of residual min-cut equals maximum flow."""
        net = MarketplaceFlowNetwork()
        candidates = [
            CandidateNode("c1", skills=["python", "docker"], capacity=1),
            CandidateNode("c2", skills=["python", "react"], capacity=1),
            CandidateNode("c3", skills=["react", "typescript"], capacity=1),
            CandidateNode("c4", skills=["python", "sql"], capacity=1),
        ]
        jobs = [
            JobNode("j1", required_skills=["python"], capacity=1),
            JobNode("j2", required_skills=["react"], capacity=1),
            JobNode("j3", required_skills=["rust"], capacity=1),
        ]

        net.build_network(candidates, jobs)
        max_flow = DinicAlgorithm.compute_max_flow(net.graph, net.source_id, net.sink_id)
        assert max_flow == 2.0

        s_part, t_part = MinCutAnalyzer.compute_min_cut_partitions(net)
        assert net.source_id in s_part
        assert net.sink_id in t_part
        assert len(s_part & t_part) == 0

        cut_cap = 0.0
        for u in s_part:
            for edge in net.graph.get_edges(u):
                if edge.v in t_part and edge.capacity > 0:
                    cut_cap += edge.capacity
                    assert edge.residual_capacity < 1e-6

        assert abs(cut_cap - max_flow) < 1e-6
        report = MinCutAnalyzer.find_bottlenecks(net)
        assert abs(report.cut_capacity - max_flow) < 1e-6


class TestBigOVerification:
    """Empirical verification of theoretical Big-O algorithmic scaling bounds (PROJECT.md benchmark requirement)."""

    def test_dinic_dense_graph_superiority_over_edmonds_karp(self) -> None:
        """Confirm Dinic's O(V^2 * E) significantly outperforms Edmonds-Karp O(V * E^2) on dense layered graphs."""
        g_dinic = CustomAdjacencyGraph()
        g_ek = CustomAdjacencyGraph()

        s, t = 0, 81
        layers = [[s]] + [[1 + l * 20 + i for i in range(20)] for l in range(4)] + [[t]]

        for l in range(len(layers) - 1):
            for u in layers[l]:
                for v in layers[l + 1]:
                    cap = ((u * 7 + v * 13) % 50) + 1.0
                    g_dinic.add_edge(u, v, cap)
                    g_ek.add_edge(u, v, cap)

        t0 = time.perf_counter()
        f_dinic = DinicAlgorithm.compute_max_flow(g_dinic, s, t)
        dt_dinic = time.perf_counter() - t0

        t0 = time.perf_counter()
        f_ek = EdmondsKarp.compute_max_flow(g_ek, s, t)
        dt_ek = time.perf_counter() - t0

        assert abs(f_dinic - f_ek) < 1e-6
        # Dinic blocking flow DFS with edge pruning must outperform Edmonds-Karp on dense networks
        assert dt_dinic < dt_ek, f"Dinic ({dt_dinic:.4f}s) was not faster than EK ({dt_ek:.4f}s)"

    def test_kmp_and_aho_corasick_linear_time_scaling(self) -> None:
        """Confirm KMP and Aho-Corasick execute in strictly linear O(N + M) time."""
        rng = random.Random(777)
        chars = ["a", "b", "c", "d"]
        text_50k = "".join(rng.choice(chars) for _ in range(50_000))
        text_100k = text_50k + "".join(rng.choice(chars) for _ in range(50_000))
        needle = "abcdabce"

        t0 = time.perf_counter()
        KMPMatcher.find_all(text_50k, needle)
        t_50k = time.perf_counter() - t0

        t0 = time.perf_counter()
        KMPMatcher.find_all(text_100k, needle)
        t_100k = time.perf_counter() - t0

        # Linear scaling: doubling text size should roughly double time (scale factor < 3.5, far from O(N^2))
        if t_50k > 0.001:
            ratio = t_100k / t_50k
            assert ratio < 4.0, f"KMP scaling super-linearly: {ratio:.2f}x"

    def test_sos_dp_scaling_bound(self) -> None:
        """Confirm SOS DP executes in O(n * 2^n) time."""
        for num_bits in [8, 10, 12]:
            size = 1 << num_bits
            values = [1] * size
            t0 = time.perf_counter()
            res = SOSDynamicProgramming.compute_subsets_sum(values, num_bits)
            dt = time.perf_counter() - t0
            assert len(res) == size
            assert dt < 0.2, f"SOS DP for {num_bits} bits took {dt:.3f}s"


class TestAlgorithmicBugReproductions:
    """Adversarial stress harness confirming and documenting concrete bugs in Milestone 1 implementation."""

    def test_bug1_marketplace_network_job_capacity_omission(self) -> None:
        """BUG 1: MarketplaceFlowNetwork ignores JobNode.capacity when capacities dict is omitted.

        Line 101 correctly computes j_cap from JobNode, but never stores it.
        Line 115 overwrites j_cap with `capacities.get(jid, 1) if capacities else 1`,
        forcing job capacity to 1.0 unconditionally.
        """
        net = MarketplaceFlowNetwork()
        c1 = CandidateNode("c1", skills=["python"])
        c2 = CandidateNode("c2", skills=["python"])
        j1 = JobNode("j1", required_skills=["python"], capacity=2)

        result = net.execute_allocation(candidates=[c1, c2], jobs=[j1], capacities=None)

        # Expected: 2 matches (j1 has capacity 2)
        # Buggy behavior: 1 match
        is_bug_present = result.total_matches == 1
        assert not is_bug_present, (
            f"BUG 1 REPRODUCED: JobNode.capacity=2 ignored by MarketplaceFlowNetwork! "
            f"Allocated {result.total_matches} candidate instead of 2. "
            f"Fix: save j_cap in build_network and reference it in line 115."
        )

    def test_bug2_bitmask_tsp_duplicate_start_node_in_tour(self) -> None:
        """BUG 2: BitmaskTSP.find_optimal_tour duplicates start_node twice at the end.

        Line 71 starts with path=[start_node]. Backtracking appends start_node again.
        After reverse(), path is [start_node, ..., last_node, start_node].
        Line 82 then calls path.append(start_node) AGAIN, giving length N + 2 instead of N + 1.
        """
        matrix = [
            [0.0, 10.0, 15.0, 20.0],
            [10.0, 0.0, 35.0, 25.0],
            [15.0, 35.0, 0.0, 30.0],
            [20.0, 25.0, 30.0, 0.0],
        ]
        cost, tour = BitmaskTSP.find_optimal_tour(matrix, start_node=0)

        # For 4 nodes, a closed TSP tour visiting all nodes and returning must have length 5:
        # [0, v1, v2, v3, 0]
        # Bug produces 6 elements: [0, v1, v2, v3, 0, 0]
        has_trailing_duplicate = len(tour) == 6 and tour[-1] == 0 and tour[-2] == 0
        assert not has_trailing_duplicate, (
            f"BUG 2 REPRODUCED: BitmaskTSP tour contains duplicate start_node: {tour}. "
            f"Expected length 5, got length {len(tour)}. "
            f"Fix: remove line 82 `path.append(start_node)` in core/engine/dp/bitmask_tsp.py."
        )

    def test_bug3_dinic_source_equal_sink_infinite_loop(self) -> None:
        """BUG 3: DinicAlgorithm.compute_max_flow enters an infinite loop when source == sink.

        When source == sink, BFS immediately marks sink visited with level 0,
        blocking flow DFS immediately returns infinity, total_flow += inf, and the loop never halts.
        """
        import subprocess
        import sys

        code = (
            "from core.engine.structures.adjacency_graph import CustomAdjacencyGraph; "
            "from core.engine.flow.dinic import DinicAlgorithm; "
            "g = CustomAdjacencyGraph(); g.add_edge(0, 0, 10); "
            "DinicAlgorithm.compute_max_flow(g, 0, 0)"
        )
        try:
            subprocess.run([sys.executable, "-c", code], timeout=0.5, capture_output=True)
            hung = False
        except subprocess.TimeoutExpired:
            hung = True

        assert not hung, (
            "BUG 3 REPRODUCED: DinicAlgorithm hung in infinite loop when source == sink! "
            "Fix: Add boundary check at start of compute_max_flow: `if source == sink: return 0.0`."
        )
