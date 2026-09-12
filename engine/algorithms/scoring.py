from typing import Any, Dict, List, Tuple

from engine.algorithms.skill_normalization import cosine_similarity


def propagation_credit(dist: int) -> float:
    if dist == 0:
        return 1.0  # exact
    if dist == 1:
        return 0.6  # parent/child
    if dist == 2:
        return 0.3  # sibling
    return 0.0


class OntologyDistanceTable:
    def __init__(self) -> None:
        self.distances: Dict[Tuple[str, str], int] = {}

    def add_distance(self, s1: str, s2: str, dist: int) -> None:
        self.distances[(s1, s2)] = dist
        self.distances[(s2, s1)] = dist

    def lookup(self, s1: str, s2: str) -> int:
        if s1 == s2:
            return 0
        return self.distances.get((s1, s2), 999)


def seniority_penalty(candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
    # Dummy implementation for seniority alignment
    return 1.0


def lookup_historical_acceptance(
    cand_cluster: Optional[str], job_cluster: Optional[str]
) -> float:
    return 0.5


def recency_score(parsed_at: Optional[Any]) -> float:
    return 1.0


def cosine(v1: List[float], v2: List[float]) -> float:
    return cosine_similarity(v1, v2)


def fit_score(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    ontology_distance_table: OntologyDistanceTable,
    weights: Dict[str, float],
) -> Tuple[float, Dict[str, Any]]:
    hard_total, hard_covered = 0.0, 0.0
    soft_total, soft_covered = 0.0, 0.0
    matched: List[Dict[str, Any]] = []

    for req in job.get("required_skills", []):
        w = float(req.get("weight", 1.0))
        is_hard = bool(req.get("hard_constraint", False))
        if is_hard:
            hard_total += w
        else:
            soft_total += w

        best_credit = 0.0
        for mention in candidate.get("skills", []):
            dist = ontology_distance_table.lookup(
                mention.get("canonical_skill_id", ""), req.get("canonical_skill_id", "")
            )
            credit = propagation_credit(dist)

            y_exp = mention.get("years_experience")
            req_min = req.get("min_years")
            if y_exp is not None and req_min is not None and req_min > 0:
                credit *= min(1.0, float(y_exp) / float(req_min))
            best_credit = max(best_credit, credit)

        if is_hard:
            hard_covered += w * best_credit
            if best_credit == 0.0:
                return 0.0, {}  # hard fail
        else:
            soft_covered += w * best_credit

        if best_credit > 0:
            matched.append(
                {"skill": req.get("canonical_skill_id"), "credit": best_credit}
            )

    hard_skill_coverage = hard_covered / max(hard_total, 1.0)
    soft_skill_coverage = soft_covered / max(soft_total, 1.0)

    skill_depth_bonus = (
        sum(m["credit"] for m in matched) / max(len(matched), 1.0) if matched else 0.0
    )

    semantic_similarity = cosine(
        candidate.get("embedding_vector", []), job.get("embedding_vector", [])
    )
    seniority_alignment = seniority_penalty(candidate, job)
    location_fit = 1.0
    historical_signal = lookup_historical_acceptance(
        candidate.get("profile_cluster"), job.get("profile_cluster")
    )
    recency = recency_score(candidate.get("parsed_at"))

    score = (
        weights.get("hard", 0.3) * hard_skill_coverage
        + weights.get("soft", 0.15) * soft_skill_coverage
        + weights.get("depth", 0.1) * skill_depth_bonus
        + weights.get("semantic", 0.15) * semantic_similarity
        + weights.get("seniority", 0.1) * seniority_alignment
        + weights.get("location", 0.05) * location_fit
        + weights.get("historical", 0.1) * historical_signal
        + weights.get("recency", 0.05) * recency
    )

    explanation = {
        "hard_skill_coverage": hard_skill_coverage,
        "soft_skill_coverage": soft_skill_coverage,
        "matched": matched,
        "semantic_similarity": semantic_similarity,
    }

    return score, explanation
