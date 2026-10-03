"""Unit tests for String Matching and Processing Algorithms (DSA Module M2).

Verifies KMPMatcher, ZAlgorithm, RabinKarp, AhoCorasickAutomaton, and SuffixArray + KasaiLCP.
"""

from core.engine.string.aho_corasick import AhoCorasickAutomaton
from core.engine.string.kmp import KMPMatcher
from core.engine.string.rabin_karp import RabinKarp
from core.engine.string.suffix_array import KasaiLCP, SuffixArray
from core.engine.string.z_algorithm import ZAlgorithm

# ==============================================================================
# 1. KMPMatcher Tests
# ==============================================================================


def test_kmp_failure_function():
    pi = KMPMatcher.compute_prefix_function("ABABAC")
    assert pi == [0, 0, 1, 2, 3, 0]

    pi_a = KMPMatcher.compute_prefix_function("AAAA")
    assert pi_a == [0, 1, 2, 3]


def test_kmp_search_occurrences():
    text = "AABAACAADAABAABA"
    pattern = "AABA"
    matches = KMPMatcher.find_all(text, pattern)
    assert matches == [0, 9, 12]

    assert KMPMatcher.find_first(text, pattern) == 0
    assert KMPMatcher.find_first(text, "XYZ") == -1
    assert KMPMatcher.count_occurrences(text, pattern) == 3


def test_kmp_edge_cases():
    assert KMPMatcher.find_all("", "abc") == []
    assert KMPMatcher.find_all("abc", "") == []
    assert KMPMatcher.find_all("short", "longer_pattern") == []


# ==============================================================================
# 2. ZAlgorithm Tests
# ==============================================================================


def test_z_algorithm_construction():
    s = "aabzaa"
    z = ZAlgorithm.compute_z_array(s)
    # Z[0] = 6, Z[1] = 1 ('a'), Z[2] = 0 ('b'), Z[3] = 0 ('z'), Z[4] = 2 ("aa"), Z[5] = 1 ('a')
    assert z[0] == 6
    assert z[1] == 1
    assert z[2] == 0
    assert z[3] == 0
    assert z[4] == 2
    assert z[5] == 1


def test_z_algorithm_pattern_search():
    text = "GEEKS FOR GEEKS"
    pattern = "GEEKS"
    matches = ZAlgorithm.search(text, pattern)
    assert matches == [0, 10]


# ==============================================================================
# 3. RabinKarp Tests
# ==============================================================================


def test_rabin_karp_pattern_search():
    text = "the quick brown fox jumps over the lazy dog"
    assert RabinKarp.find_all(text, "the") == [0, 31]
    assert RabinKarp.find_all(text, "fox") == [16]
    assert RabinKarp.find_all(text, "cat") == []


def test_rabin_karp_duplicate_detection():
    doc1 = "Software engineer proficient in Python, FastAPI, Docker, and PostgreSQL databases."
    doc2 = "Senior developer experienced in Python, FastAPI, Docker, and Kubernetes deployment."

    # Substring "Python, FastAPI, Docker, and " is 29 chars long
    duplicates = RabinKarp.detect_duplicates(doc1, doc2, k=20)
    assert len(duplicates) > 0
    assert any("Python, FastAPI" in d["content"] for d in duplicates)

    # Identical documents have similarity 1.0
    assert RabinKarp.similarity_score(doc1, doc1, k=10) == 1.0

    # Completely disjoint documents
    assert RabinKarp.similarity_score("AAAAAAAAAA", "BBBBBBBBBB", k=5) == 0.0


# ==============================================================================
# 4. AhoCorasickAutomaton Tests
# ==============================================================================


def test_aho_corasick_classic_matching():
    ac = AhoCorasickAutomaton()
    keywords = ["he", "she", "his", "hers"]
    for kw in keywords:
        ac.add_word(kw, payload=kw.upper())

    ac.build()
    text = "ushers"
    matches = ac.find_all(text)

    # In "ushers":
    # at index 1..4: "she"
    # at index 2..4: "he"
    # at index 2..6: "hers"
    matched_words = [m.word for m in matches]
    assert "she" in matched_words
    assert "he" in matched_words
    assert "hers" in matched_words

    extracted = ac.extract_keywords(text)
    assert set(extracted) == {"she", "he", "hers"}


def test_aho_corasick_large_skill_dictionary():
    ac = AhoCorasickAutomaton(ignore_case=True)
    skills = [
        "python",
        "react",
        "fastapi",
        "docker",
        "kubernetes",
        "postgresql",
        "redis",
        "typescript",
        "graphql",
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "git",
        "ci/cd",
        "linux",
    ]
    for s in skills:
        ac.add_word(s, payload=s)

    ac.build()
    resume_text = (
        "Senior Software Engineer experienced with Python, FastAPI, and Docker. "
        "Built microservices deployed on Kubernetes with PostgreSQL and Redis backends. "
        "Strong background in machine learning and TypeScript."
    )

    found = ac.extract_keywords(resume_text)
    assert "python" in found
    assert "fastapi" in found
    assert "docker" in found
    assert "kubernetes" in found
    assert "postgresql" in found
    assert "redis" in found
    assert "machine learning" in found
    assert "typescript" in found


# ==============================================================================
# 5. SuffixArray and KasaiLCP Tests
# ==============================================================================


def test_suffix_array_banana():
    s = "banana"
    sa = SuffixArray(s).get_suffix_array()
    assert sa == [5, 3, 1, 0, 4, 2]

    lcp = KasaiLCP.compute_lcp(s, sa)
    # LCP between adjacent sorted suffixes:
    # sa[0]=5 ("a"), sa[1]=3 ("ana"): LCP=1
    # sa[1]=3 ("ana"), sa[2]=1 ("anana"): LCP=3
    # sa[2]=1 ("anana"), sa[3]=0 ("banana"): LCP=0
    # sa[3]=0 ("banana"), sa[4]=4 ("na"): LCP=0
    # sa[4]=4 ("na"), sa[5]=2 ("nana"): LCP=2
    assert lcp == [0, 1, 3, 0, 0, 2]

    assert KasaiLCP.longest_repeated_substring("banana") == "ana"


def test_longest_common_substring():
    s1 = "photocopy"
    s2 = "copyright"
    lcs = KasaiLCP.longest_common_substring(s1, s2)
    assert lcs == "copy"
