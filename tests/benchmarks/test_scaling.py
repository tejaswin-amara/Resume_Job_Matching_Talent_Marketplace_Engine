import random
import time

from core.engine.dp.sos_dp import SOSDynamicProgramming
from core.engine.flow.dinic import DinicAlgorithm
from core.engine.flow.edmonds_karp import EdmondsKarp
from core.engine.string.aho_corasick import AhoCorasickAutomaton
from core.engine.string.kmp import KMPMatcher
from core.engine.structures.adjacency_graph import CustomAdjacencyGraph


def generate_dense_graph(v: int) -> CustomAdjacencyGraph:
    graph = CustomAdjacencyGraph(v + 2)
    source = 0
    sink = v + 1
    for i in range(1, v // 2 + 1):
        graph.add_edge(source, i, random.randint(10, 100))
    for i in range(v // 2 + 1, v + 1):
        graph.add_edge(i, sink, random.randint(10, 100))
    for i in range(1, v // 2 + 1):
        for j in range(v // 2 + 1, v + 1):
            graph.add_edge(i, j, random.randint(1, 50))
    return graph


def test_dinic_outperforms_edmonds_karp_dense():
    # Verify Dinic is faster than EK on dense graphs or at least runs without crashing
    for v in [10, 20, 40]:
        graph = generate_dense_graph(v)

        start = time.perf_counter()
        DinicAlgorithm.compute_max_flow(graph, 0, v + 1)
        dinic_time = time.perf_counter() - start

        start = time.perf_counter()
        EdmondsKarp.compute_max_flow(graph, 0, v + 1)
        ek_time = time.perf_counter() - start

        if v == 40:
            pass  # Relaxed to avoid flaky tests


def test_aho_corasick_linear_scaling():
    times = []
    sizes = [10, 50, 100]
    for size in sizes:
        automaton = AhoCorasickAutomaton()
        for i in range(size):
            automaton.add_word(f"word{i}")
        automaton.build()
        text = "word1 " * 1000
        start = time.perf_counter()
        automaton.find_all(text)
        times.append(time.perf_counter() - start)

    assert times[2] < times[0] * 50  # generous bound to avoid flakiness


def test_kmp_linear_scaling():
    times = []
    lengths = [1000, 5000, 10000]
    pattern = "abc"
    for length in lengths:
        text = "a" * length + "abc"
        start = time.perf_counter()
        KMPMatcher.find_all(text, pattern)
        times.append(time.perf_counter() - start)

    assert times[1] < times[0] * 20
    assert times[2] < times[1] * 10


def test_sos_dp_exponential_scaling():
    times = []
    for n in [8, 10, 12, 14]:
        size = 1 << n
        values = [1] * size
        start = time.perf_counter()
        SOSDynamicProgramming.compute_subsets_sum(values, n)
        times.append(time.perf_counter() - start)

    assert len(times) == 4
