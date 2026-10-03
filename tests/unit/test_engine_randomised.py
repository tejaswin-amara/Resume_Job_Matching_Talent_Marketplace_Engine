"""Unit tests for Randomized and Parallel Algorithmic Primitives (DSA Module M6).

Verifies ReservoirSampler, MillerRabin, UniversalHashFamily, and ParallelPrimitives (Blelloch scan).
"""

import pytest

from core.engine.randomised.miller_rabin import MillerRabin, UniversalHashFamily
from core.engine.randomised.parallel_primitives import ParallelPrimitives
from core.engine.randomised.reservoir_sampling import ReservoirSampler

# ==============================================================================
# 1. ReservoirSampler Tests (Algorithm R)
# ==============================================================================


def test_reservoir_sampler_streaming():
    sampler = ReservoirSampler[int](k=5, seed=42)
    # Stream 100 items
    for i in range(100):
        sampler.add(i)

    sample = sampler.get_sample()
    assert len(sample) == 5
    assert all(0 <= x < 100 for x in sample)
    assert len(set(sample)) == 5  # Distinct elements


def test_reservoir_sampler_edge_cases():
    with pytest.raises(ValueError):
        ReservoirSampler[int](k=0)

    # Stream shorter than reservoir capacity
    sample = ReservoirSampler.sample_stream([1, 2, 3], k=5)
    assert sample == [1, 2, 3]


def test_reservoir_sampler_uniformity():
    # Statistical check: with 1000 trials sampling 1 item from [0, 1, 2],
    # each item should be chosen roughly 333 times (+- 60)
    counts = [0, 0, 0]
    for trial in range(1000):
        s = ReservoirSampler.sample_stream([0, 1, 2], k=1, seed=trial)
        counts[s[0]] += 1

    for c in counts:
        assert 250 <= c <= 420


# ==============================================================================
# 2. MillerRabin & UniversalHashFamily Tests
# ==============================================================================


def test_miller_rabin_primes_and_composites():
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 101, 1000000007]
    for p in primes:
        assert MillerRabin.is_prime(p), f"Expected {p} to be identified as prime"

    composites = [0, 1, 4, 6, 8, 9, 10, 15, 21, 25, 27, 561]  # 561 is Carmichael number
    for c in composites:
        assert not MillerRabin.is_prime(c), f"Expected {c} to be identified as composite"

    assert MillerRabin.next_prime(10) == 11
    assert MillerRabin.next_prime(19) == 23


def test_universal_hash_family():
    uhf = UniversalHashFamily(m=100, seed=123)
    val = uhf.hash_int(42)
    assert 0 <= val < 100

    str_val = uhf.hash_string("candidate_credential_hash")
    assert 0 <= str_val < 100

    # Fingerprint format
    fp = uhf.generate_credential_fingerprint({"degree": "MSc Computer Science", "gpa": 3.9})
    assert fp.startswith("CR-")
    assert len(fp) >= 12


# ==============================================================================
# 3. ParallelPrimitives Tests (Blelloch Scan & Tree Reduction)
# ==============================================================================


def test_blelloch_parallel_scan():
    # Input array of length 8
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    res = ParallelPrimitives.blelloch_scan(data)

    # Prefix sums:
    # Exclusive: [0, 1, 3, 6, 10, 15, 21, 28]
    # Inclusive: [1, 3, 6, 10, 15, 21, 28, 36]
    assert res.exclusive_scan == [0, 1, 3, 6, 10, 15, 21, 28]
    assert res.inclusive_scan == [1, 3, 6, 10, 15, 21, 28, 36]

    # Metrics verification
    # For N=8: Up-sweep work = 4 + 2 + 1 = 7 ops, Down-sweep work = 2*(1 + 2 + 4) = 14 ops -> total work = 21 ops
    # Span = log2(8) + log2(8) = 3 + 3 = 6
    assert res.metrics.span == 6
    assert res.metrics.work == 21
    assert res.metrics.parallelism > 1.0


def test_blelloch_scan_non_power_of_two():
    # Non-power-of-two length
    data = [3, 1, 7, 0, 4]
    res = ParallelPrimitives.blelloch_scan(data)
    assert res.exclusive_scan == [0, 3, 4, 11, 11]
    assert res.inclusive_scan == [3, 4, 11, 11, 15]


def test_tree_reduce():
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    res = ParallelPrimitives.tree_reduce(data)
    assert res.value == 36
    assert res.metrics.span == 3  # log2(8) = 3
    assert res.metrics.work == 7  # 4 + 2 + 1 = 7 ops
