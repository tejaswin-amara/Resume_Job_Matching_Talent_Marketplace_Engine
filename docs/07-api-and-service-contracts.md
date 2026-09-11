## 7. API and Service Contracts

### 7.1 Core Endpoints

```
POST   /v1/resumes                     — upload/create a resume (multipart or JSON)
GET    /v1/resumes/{resume_id}         — fetch parsed resume (access-controlled)
POST   /v1/jobs                        — create a job posting
GET    /v1/jobs/{job_id}               — fetch a job posting
GET    /v1/jobs/{job_id}/matches       — ranked candidate matches for a job (Sec.3)
         query params: top_k, min_score, include_explanation
GET    /v1/candidates/{candidate_id}/matches — ranked job matches for a candidate
POST   /v1/allocations/run             — trigger an allocation batch (Sec.4)
         body: { team_id | job_ids[], strategy: "max_weight"|"stable" }
GET    /v1/allocations/{run_id}        — allocation run result + status
POST   /v1/teams/{team_id}/min-skill-set — compute minimum viable skill set (Sec.5)
GET    /v1/skills                      — search/browse skill ontology
POST   /v1/skills/aliases              — (admin) submit/curate an alias mapping
```

### 7.2 Example I/O

```jsonc
// GET /v1/jobs/{job_id}/matches?top_k=10&include_explanation=true
Response 200:
{
  "job_id": "job_123",
  "model_version": "scorer-2026.08.1",
  "matches": [
    {
      "candidate_id": "cand_987",
      "score": 0.87,
      "explanation": {
        "hard_skill_coverage": 1.0,
        "soft_skill_coverage": 0.6,
        "matched_skills": [
          {"skill": "skill:react_js", "match_type": "exact", "years": 4},
          {"skill": "skill:graphql", "match_type": "parent(api_design)", "years": null}
        ],
        "missing_hard_skills": [],
        "semantic_similarity": 0.81
      }
    }
  ]
}
```

### 7.3 Authentication & Rate Limits

- **AuthN**: OAuth2 / signed JWT per caller (candidate, employer, admin service account); mTLS between internal services.
- **AuthZ**: role-based — candidates can only read/write their own resume; employers can only read matches for their own postings and never see another employer's raw candidate pool directly (only ranked results for their job); admins have ontology-curation and audit-log access.
- **Rate limits**: per-API-key token bucket, e.g. 100 req/min for `/matches` endpoints, 10 req/min for `/allocations/run` (expensive batch op — also queued, not synchronous, above a size threshold).

### 7.4 Observability

- **Logging**: structured JSON logs per request including `request_id`, `model_version`, `latency_ms`, `caller_role`; scoring calls additionally log the full feature vector (Sec.3/8) to a write-once audit store.
- **Metrics**: latency histograms (p50/p95/p99) per endpoint, index query QPS, cache hit ratio, allocation-batch runtime, fairness-parity metrics (Sec.3.3) on a rolling dashboard.
- **Tracing**: distributed tracing (span per pipeline stage: retrieval → scoring → response) with a trace ID propagated end-to-end, so a slow match query can be attributed to a specific stage (e.g., embedding ANN lookup vs. inverted-index intersection).

---

