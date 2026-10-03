"""String matching and analysis algorithms.

Zero-library constraint: built strictly from primitive arrays and pointer loops.
"""

from core.engine.string.aho_corasick import AhoCorasickAutomaton, AhoMatch
from core.engine.string.kmp import KMPMatcher
from core.engine.string.rabin_karp import RabinKarp
from core.engine.string.suffix_array import KasaiLCP, SuffixArray
from core.engine.string.z_algorithm import ZAlgorithm

__all__ = [
    "AhoCorasickAutomaton",
    "AhoMatch",
    "KMPMatcher",
    "KasaiLCP",
    "RabinKarp",
    "SuffixArray",
    "ZAlgorithm",
]
