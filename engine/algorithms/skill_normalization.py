import math
from typing import Any


def edit_distance(a: str, b: str) -> int:
    """
    Wagner-Fischer edit distance for fuzzy skill/company normalization.
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost,  # substitution
            )
    return dp[n][m]


def threshold_edit(length: int) -> int:
    return 1 if length <= 5 else 2


class AliasTrieNode:
    def __init__(self) -> None:
        self.children: dict[str, AliasTrieNode] = {}
        self.skill_id: str | None = None


class AliasTrie:
    def __init__(self) -> None:
        self.root = AliasTrieNode()
        self.entries: list[tuple[str, str]] = []  # For fuzzy fallback simulation

    def add_alias(self, alias: str, skill_id: str) -> None:
        node = self.root
        for char in alias:
            if char not in node.children:
                node.children[char] = AliasTrieNode()
            node = node.children[char]
        node.skill_id = skill_id
        self.entries.append((alias, skill_id))

    def exact_lookup(self, key: str) -> AliasTrieNode | None:
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        return node if node.skill_id else None

    def all_entries_within_length_window(
        self, key: str, window: int = 3
    ) -> list[tuple[str, str]]:
        return [(a, s) for a, s in self.entries if abs(len(a) - len(key)) <= window]


def strip_and_lowercase(raw_token: str) -> str:
    return "".join(e for e in raw_token if e.isalnum() or e.isspace()).lower().strip()


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


class OntologyEmbeddings:
    def __init__(self) -> None:
        self.skills: dict[str, list[float]] = {}

    def add_embedding(self, skill_id: str, vector: list[float]) -> None:
        self.skills[skill_id] = vector

    def nearest_neighbor(self, vec: list[float]) -> tuple[str | None, float]:
        best_sim = -1.0
        best_skill = None
        for skill_id, s_vec in self.skills.items():
            sim = cosine_similarity(vec, s_vec)
            if sim > best_sim:
                best_sim = sim
                best_skill = skill_id
        return best_skill, best_sim


def dummy_embed(key: str) -> list[float]:
    # Dummy embedding for testing tier 3
    import random

    return [random.random() for _ in range(128)]


def normalize_skill(
    raw_token: str,
    alias_trie: AliasTrie,
    ontology_embeddings: OntologyEmbeddings,
    threshold_cos: float = 0.8,
) -> dict[str, Any]:
    """
    Normalizes a raw skill string into a canonical skill ID using a three-tier approach:
    Tier 1: Exact string match using an alias trie.
    Tier 2: Bounded fuzzy match using edit distance.
    Tier 3: Semantic embedding match using cosine similarity.

    Args:
        raw_token: The raw skill string to normalize.
        alias_trie: The alias trie data structure.
        ontology_embeddings: The ontology embeddings for semantic match.
        threshold_cos: The cosine similarity threshold for semantic matches.

    Returns:
        A dictionary containing the canonical 'skill_id', 'confidence' score, and matched 'tier'.
    """
    key = strip_and_lowercase(raw_token)

    # Tier 1: exact trie lookup
    if (node := alias_trie.exact_lookup(key)) is not None:
        return {"skill_id": node.skill_id, "confidence": 1.0, "tier": 1}

    # Tier 2: bounded fuzzy match
    best: dict[str, Any] | None = None
    for candidate_alias, skill_id in alias_trie.all_entries_within_length_window(key):
        d = edit_distance(key, candidate_alias)
        if d <= threshold_edit(len(candidate_alias)) and (
            best is None or d < best["distance"]
        ):
            best = {"skill_id": skill_id, "distance": d}

    if best is not None:
        return {
            "skill_id": best["skill_id"],
            "confidence": 1.0 - float(best["distance"]) / max(len(key), 1),
            "tier": 2,
        }

    # Tier 3: semantic embedding
    vec = dummy_embed(key)
    nearest_skill_id, cos_sim = ontology_embeddings.nearest_neighbor(vec)
    if cos_sim >= threshold_cos:
        return {"skill_id": nearest_skill_id, "confidence": cos_sim, "tier": 3}

    # No confident match
    return {"skill_id": None, "confidence": 0.0, "tier": 0}
