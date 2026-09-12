from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI
from pydantic import BaseModel

from algorithms.allocation import (allocate_min_cost_flow, greedy_set_cover,
                                   min_candidates_to_cover)
from algorithms.scoring import OntologyDistanceTable, fit_score
from algorithms.skill_normalization import (AliasTrie, OntologyEmbeddings,
                                            normalize_skill)

app = FastAPI(title="Talent Engine Algorithms API")

# In-memory models for testing
alias_trie: AliasTrie = AliasTrie()
ontology_embeddings: OntologyEmbeddings = OntologyEmbeddings()
distance_table: OntologyDistanceTable = OntologyDistanceTable()


class NormalizeRequest(BaseModel):
    raw_token: str


@app.post("/api/v1/algorithms/normalize")
def api_normalize(req: NormalizeRequest) -> Dict[str, Any]:
    return normalize_skill(req.raw_token, alias_trie, ontology_embeddings)


class ScoringRequest(BaseModel):
    candidate: Dict[str, Any]
    job: Dict[str, Any]
    weights: Dict[str, float]


@app.post("/api/v1/algorithms/score")
def api_score(req: ScoringRequest) -> Dict[str, Any]:
    score, expl = fit_score(req.candidate, req.job, distance_table, req.weights)
    return {"score": score, "explanation": expl}


class AllocationRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    fit_scores: Dict[str, float]  # key format: "cand_id:job_id"


@app.post("/api/v1/algorithms/allocate")
def api_allocate(req: AllocationRequest) -> Dict[str, Any]:
    # Convert fit_scores dict string keys to tuple keys
    scores: Dict[Tuple[str, str], float] = {}
    for k, v in req.fit_scores.items():
        parts = k.split(":")
        if len(parts) == 2:
            scores[(parts[0], parts[1])] = v
    assignments = allocate_min_cost_flow(req.candidates, req.jobs, req.teams, scores)
    return {"assignments": [{"candidate_id": c, "job_id": j} for c, j in assignments]}


class MinCoverRequest(BaseModel):
    skills_universe: List[str]
    candidates: List[Dict[str, Any]]


@app.post("/api/v1/algorithms/min-cover/exact")
def api_min_cover_exact(req: MinCoverRequest) -> Dict[str, Any]:
    skill_to_bit = {s: i for i, s in enumerate(req.skills_universe)}
    masks = []
    for c in req.candidates:
        m = 0
        for s in c.get("skills", []):
            if s in skill_to_bit:
                m |= 1 << skill_to_bit[s]
        masks.append(m)
    chosen_idx = min_candidates_to_cover(req.skills_universe, masks)
    if chosen_idx is None:
        return {"infeasible": True}
    return {"chosen_candidates": [req.candidates[i] for i in chosen_idx]}


@app.post("/api/v1/algorithms/min-cover/greedy")
def api_min_cover_greedy(req: MinCoverRequest) -> Dict[str, Any]:
    def cost_fn(c: Dict[str, Any]) -> float:
        return c.get("cost", 1.0)

    res = greedy_set_cover(set(req.skills_universe), req.candidates, cost_fn)
    return res
