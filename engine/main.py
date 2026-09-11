from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from algorithms.skill_normalization import normalize_skill, AliasTrie, OntologyEmbeddings
from algorithms.scoring import fit_score, OntologyDistanceTable
from algorithms.allocation import allocate_min_cost_flow, min_candidates_to_cover, greedy_set_cover

app = FastAPI(title="Talent Engine Algorithms API")

# In-memory models for testing
alias_trie = AliasTrie()
ontology_embeddings = OntologyEmbeddings()
distance_table = OntologyDistanceTable()

class NormalizeRequest(BaseModel):
    raw_token: str

@app.post("/api/v1/algorithms/normalize")
def api_normalize(req: NormalizeRequest):
    return normalize_skill(req.raw_token, alias_trie, ontology_embeddings)

class ScoringRequest(BaseModel):
    candidate: dict
    job: dict
    weights: dict

@app.post("/api/v1/algorithms/score")
def api_score(req: ScoringRequest):
    score, expl = fit_score(req.candidate, req.job, distance_table, req.weights)
    return {"score": score, "explanation": expl}

class AllocationRequest(BaseModel):
    candidates: List[dict]
    jobs: List[dict]
    teams: List[dict]
    fit_scores: Dict[str, float] # key format: "cand_id:job_id"

@app.post("/api/v1/algorithms/allocate")
def api_allocate(req: AllocationRequest):
    # Convert fit_scores dict string keys to tuple keys
    scores = {}
    for k, v in req.fit_scores.items():
        parts = k.split(':')
        if len(parts) == 2:
            scores[(parts[0], parts[1])] = v
    assignments = allocate_min_cost_flow(req.candidates, req.jobs, req.teams, scores)
    return {"assignments": [{"candidate_id": c, "job_id": j} for c, j in assignments]}

class MinCoverRequest(BaseModel):
    skills_universe: List[str]
    candidates: List[dict]

@app.post("/api/v1/algorithms/min-cover/exact")
def api_min_cover_exact(req: MinCoverRequest):
    skill_to_bit = {s: i for i, s in enumerate(req.skills_universe)}
    masks = []
    for c in req.candidates:
        m = 0
        for s in c.get('skills', []):
            if s in skill_to_bit:
                m |= (1 << skill_to_bit[s])
        masks.append(m)
    chosen_idx = min_candidates_to_cover(req.skills_universe, masks)
    if chosen_idx is None:
        return {"infeasible": True}
    return {"chosen_candidates": [req.candidates[i] for i in chosen_idx]}

@app.post("/api/v1/algorithms/min-cover/greedy")
def api_min_cover_greedy(req: MinCoverRequest):
    def cost_fn(c): return c.get('cost', 1.0)
    res = greedy_set_cover(set(req.skills_universe), req.candidates, cost_fn)
    return res
