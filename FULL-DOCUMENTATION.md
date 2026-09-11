# Résumé–Job Matching & Talent-Marketplace Engine
## Full Engineering Documentation Package (single-file view)

> Auto-generated from `docs/*.md` by `scripts/build_full_documentation.py`.
> Do not hand-edit this file directly — edit the relevant file under `docs/` and regenerate.

---

## 1. System Overview

### 1.1 Objectives

| # | Objective | Metric |
|---|---|---|
| O1 | Match candidates to job postings with high relevance | Precision@10 ≥ 0.75, Recall@50 ≥ 0.85 |
| O2 | Rank candidates for a given role fairly and explainably | 100% of scores traceable to feature contributions |
| O3 | Assign candidates to open roles / teams optimally at scale | Stable, envy-minimizing assignment on ≥10⁵ candidate–role pairs in <60s batch |
| O4 | Compute the minimum viable skill set to staff a team | Exact for small teams (≤20 roles), ≥95%-optimal approximation for large teams |
| O5 | Operate at millions-of-records scale with sub-200ms query latency | p95 query latency < 200ms, p99 < 500ms |
| O6 | Satisfy fairness, auditability, and data-protection requirements | Every score reproducible from a stored feature vector + model version |

### 1.2 Stakeholders

- **Candidates** — submit résumés, consent to processing, receive match explanations.
- **Employers / Hiring Managers** — post jobs, define team-composition constraints, receive ranked shortlists.
- **Talent-Ops / Marketplace Admins** — manage the skill ontology, run allocation batches, monitor fairness dashboards.
- **Compliance/Legal** — audit scoring decisions, enforce retention and consent policy.
- **Platform Engineering (this team)** — build, operate, and scale the matching engine.

### 1.3 Success Metrics (product-level)

- Time-to-shortlist (job posted → ranked candidate list): < 5 minutes end-to-end (async pipeline) / < 200ms for an already-indexed query.
- Match acceptance rate (employer marks a suggested candidate as "interview-worthy"): tracked as the primary offline/online eval signal for the scoring model.
- Fairness parity: selection-rate ratio across protected-adjacent proxy groups (only where legally permitted to measure) stays within a configured band, monitored continuously.
- Coverage: % of postings that receive at least K qualified candidates within N hours of posting.

### 1.4 High-Level Architecture

```
                                ┌─────────────────────────┐
                                │      Client Layer        │
                                │ (Web/App/Recruiter UI)   │
                                └────────────┬─────────────┘
                                             │ REST/GraphQL (Section 7)
                                ┌────────────▼─────────────┐
                                │       API Gateway         │
                                │ AuthN/AuthZ, rate limit,  │
                                │ request routing           │
                                └────────────┬─────────────┘
             ┌───────────────────────────────┼───────────────────────────────┐
             │                               │                               │
   ┌─────────▼─────────┐         ┌───────────▼───────────┐        ┌─────────▼─────────┐
   │  Ingestion Service │         │   Matching/Scoring     │        │ Allocation/Optim.  │
   │  (résumé & JD       │         │   Service               │        │ Service (bipartite │
   │   parsing, ETL)     │         │   (ranking API)         │        │ matching / flow)   │
   └─────────┬─────────┘         └───────────┬───────────┘        └─────────┬─────────┘
             │                               │                               │
   ┌─────────▼─────────────────────────────────────────────────────────────▼─────────┐
   │                          Core Data & Index Layer                                 │
   │  - Résumé Store (document DB)      - Job Store (document DB)                     │
   │  - Skill Ontology Graph (graph DB) - Inverted Index (hand-built)                  │
   │  - Embedding Index (ANN, hand-built or vetted lib per Sec 6.5)                    │
   │  - Feature Store (scoring features, versioned)                                    │
   └─────────┬─────────────────────────────────────────────────────────────┬─────────┘
             │                                                             │
   ┌─────────▼─────────┐                                         ┌─────────▼─────────┐
   │  Batch Pipeline    │                                         │  Streaming Pipeline │
   │  (nightly ETL,     │                                         │  (near-real-time    │
   │   re-embedding,    │                                         │   new-posting /     │
   │   dedup)           │                                         │   new-résumé index) │
   └────────────────────┘                                         └────────────────────┘
             │
   ┌─────────▼─────────┐
   │ Observability      │
   │ (logs/metrics/trace│
   │  + fairness audit) │
   └────────────────────┘
```

### 1.5 Module List

| Module | Responsibility | Primary algorithms (Sec.) |
|---|---|---|
| Ingestion Service | Parse résumé/JD text (PDF/DOCX/plain), extract structured fields, enrich | String matching (KMP/Z), DP edit-distance for field normalization |
| Skill Normalizer | Map raw skill tokens → canonical ontology nodes | Trie + Aho-Corasick, edit-distance fuzzy match, embedding fallback |
| Indexer | Build inverted index + embedding index | Hand-built inverted index, hashing (rolling hash for shingles) |
| Matching/Scoring Service | Compute candidate↔job fit score | Weighted feature model, DP for skill-set alignment, cosine sim |
| Allocation/Optimization Service | Assign candidates to roles under constraints | Bipartite matching (Hungarian/Hopcroft–Karp), max-flow/min-cost-flow |
| Minimum-Skill-Set Service | Derive minimal skill set to staff a team | Weighted set-cover approximation, bitmask DP for small n |
| Fairness/Audit Service | Log every scoring decision with feature attribution | Deterministic replay, no ML black box without logged features |

---

---

## 2. Data Model & Normalization

### 2.1 Core Schemas

```jsonc
// Résumé (canonical, post-parsing)
Resume {
  resume_id: UUID,
  candidate_id: UUID,
  raw_source_ref: string,          // pointer to original file in blob storage
  contact: { email_hash, phone_hash, location_geo },   // PII hashed/tokenized, see Sec.8
  summary_text: string,
  skills: [ SkillMention ],
  experience: [ ExperienceEntry ],
  education: [ EducationEntry ],
  certifications: [ string ],
  availability: { earliest_start_date, hours_per_week, remote_ok, work_auth_status },
  embedding_vector: float[d],      // dense semantic embedding of full profile
  parsed_at: timestamp,
  parser_version: string,
  consent: ConsentRecord           // see Sec.8
}

SkillMention {
  raw_text: string,                // e.g. "ReactJS", "React.js", "react"
  canonical_skill_id: string,      // FK into Skill Ontology
  confidence: float,               // normalization confidence
  years_experience: float | null,
  source_span: [start, end]        // offsets in raw resume text, for explainability
}

ExperienceEntry {
  title: string, company: string,
  start_date, end_date,
  responsibilities_text: string,
  extracted_skills: [ canonical_skill_id ]
}

// Job Posting
JobPosting {
  job_id: UUID,
  employer_id: UUID,
  title: string,
  team_id: UUID | null,            // for team-composition constraints (Sec.4/5)
  description_text: string,
  required_skills: [ SkillRequirement ],
  preferred_skills: [ SkillRequirement ],
  location: { geo, remote_policy },
  work_auth_required: [ string ],  // e.g. ["US_CITIZEN","H1B_OK"]
  seniority_level: enum,
  headcount: int,
  posted_at: timestamp,
  status: enum(open|filled|closed),
  embedding_vector: float[d]
}

SkillRequirement {
  canonical_skill_id: string,
  min_years: float | null,
  weight: float,                   // importance in scoring, 0..1
  hard_constraint: bool            // true = must-have (filters out candidate if absent)
}

// Skill Ontology (graph)
SkillNode {
  skill_id: string,                // stable canonical ID, e.g. "skill:react_js"
  display_name: string,
  aliases: [ string ],             // "reactjs","react.js","react"
  parent_ids: [ skill_id ],        // hierarchy, e.g. React -> Frontend Frameworks -> JS Ecosystem
  related_ids: [ skill_id ],       // sibling/related, weighted edges for propagation
  embedding_vector: float[d]
}
```

### 2.2 Normalization Strategy for Inconsistent Skill Terms

Three-tier normalization pipeline (cheapest/most-precise tier first, fall through on miss):

1. **Exact/alias lookup (O(1))** — hand-built hash table mapping lower-cased, punctuation-stripped raw token → canonical `skill_id`, built from the ontology's `aliases[]`. This is the dictionary trie used for tier-2 as well.
2. **Fuzzy match (edit distance / trie)** — for tokens that miss tier 1 (typos, minor variants: "Reactjs" vs "React JS"), run bounded Levenshtein (Wagner–Fischer, Sec.11) against the alias trie; accept the nearest canonical term if `edit_distance ≤ threshold(len(token))` (e.g., ≤2 for tokens >6 chars).
3. **Embedding fallback (semantic)** — for tokens that miss both above (novel terms, multi-word skill phrases, non-English variants), embed the raw phrase and do a cosine-similarity nearest-neighbor search against `SkillNode.embedding_vector`; accept above a confidence threshold, otherwise route to a **human-in-the-loop ontology-curation queue** (never silently drop or silently auto-create a node above a low-confidence bar — this protects scoring auditability).

All three tiers write `(raw_text → canonical_skill_id, confidence, tier_used)` back into an **alias-learning table**, so tier-1 coverage grows over time (self-reinforcing dictionary) without needing a human for every recurrence of a variant once it's been resolved once.

### 2.3 Skill Hierarchy / Ontology

Modeled as a **DAG** (a skill can specialize more than one parent — e.g., "PySpark" is under both "Python" and "Distributed Data Processing"). Used for:

- **Upward propagation** — a candidate who has "PyTorch" partially satisfies a job asking for the parent "Deep Learning Frameworks" at a discounted weight.
- **Downward specificity bonus** — an exact-leaf match scores higher than a parent-level match.
- **Sibling substitution** — "React" and "Vue" are siblings under "Frontend Frameworks"; sibling matches can partially satisfy a requirement at a configurable substitution weight, useful for the fairness goal of not over-penalizing transferable skill sets.

### 2.4 Indexing Strategy

| Index | Purpose | Structure |
|---|---|---|
| Inverted index (skills → résumé IDs) | Fast candidate retrieval for a required-skill set (Boolean/ranked retrieval) | Hand-built postings lists, sorted by `resume_id`, skip pointers for fast intersection (same design as classic IR inverted indexes; must be hand-built per engine constraint) |
| Inverted index (n-gram/shingle → résumé IDs) | Free-text / fuzzy title & company search | Rolling-hash (Rabin–Karp style) shingling, same postings-list structure |
| Trie (skill alias dictionary) | O(len) exact + prefix skill lookup, autocomplete | Hand-built trie, Aho-Corasick automaton for multi-skill extraction from résumé free text in one pass |
| Embedding ANN index | Semantic résumé↔job similarity, fuzzy skill fallback | HNSW-style graph index (approximate) — see Sec.6.5 for the "hand-built vs. vetted-library" boundary decision |
| Ranking signal store | Precomputed features feeding the scorer (recency, popularity, historical acceptance rate) | Columnar feature store, updated batch + streaming |

**Ranking signals used at retrieval time** (before the full scorer runs — this is a cheap first-pass filter/rank to shrink the candidate set from millions to a few thousand before the expensive scoring model runs):
- BM25-style term frequency / inverse document frequency over the skill inverted index.
- Recency of résumé update.
- Location/remote compatibility (hard filter).
- Work-authorization compatibility (hard filter).

---

---

## 3. Matching and Scoring

### 3.1 Candidate–Job Fit Scoring Model

Two-stage architecture:

**Stage A — Retrieval (cheap, high-recall).** Inverted-index Boolean/BM25 retrieval + hard-constraint filtering (location, work-auth, hard-required skills) narrows millions of résumés to a top-N (e.g., N=2,000) candidate set per job in milliseconds.

**Stage B — Scoring (expensive, high-precision).** A weighted, feature-based, linear-in-features model (chosen for **explainability** over a black-box net, per the fairness/audit requirement) computes a final score:

```
score(candidate, job) = Σ_i  w_i · f_i(candidate, job)
```

| Feature `f_i` | Description | Typical weight `w_i` |
|---|---|---|
| `hard_skill_coverage` | fraction of hard-required skills present (exact or ontology-propagated) | 0.30 |
| `soft_skill_coverage` | weighted fraction of preferred skills present | 0.15 |
| `skill_depth_bonus` | Σ over matched skills of `years_experience / min_years_required` (capped at 1) | 0.10 |
| `semantic_similarity` | cosine(candidate.embedding, job.embedding) | 0.15 |
| `seniority_alignment` | penalty for over/under-qualification vs. `seniority_level` | 0.10 |
| `location_fit` | remote/geo compatibility score (0 if hard fail, already filtered) | 0.05 |
| `historical_acceptance_signal` | learned prior: how often similar candidate→job matches converted to interviews | 0.10 |
| `recency` | freshness of résumé data | 0.05 |

Weights are **calibrated**, not hand-guessed at production time: fit via logistic regression / gradient boosting on historical (candidate, job, employer_interview_decision) labels, then the *learned* weights are frozen into the linear explainable model above (distillation of a possibly-nonlinear model into an explainable linear one is preferred to shipping the nonlinear model directly, to preserve the auditability requirement in Sec.8). Recalibrate on a monthly cadence or when feature drift exceeds a threshold (Sec.10).

### 3.2 Handling Synonyms, Expansion, and Hierarchies in Scoring

- **Synonym expansion at query time**: a job requiring `skill:react_js` is expanded, before retrieval, to the alias set `{react, reactjs, react.js, react_native? (configurable)}` via the ontology, so the inverted-index lookup doesn't miss résumés that used a different literal string.
- **Hierarchy-aware partial credit**: `hard_skill_coverage` is not binary per skill — a candidate with a **child** of the required skill gets full credit; a candidate with the **direct parent** gets partial credit (configurable, e.g. 0.6); a **sibling** gets smaller partial credit (e.g. 0.3); unrelated gets 0. This is implemented as a shortest-path lookup on the ontology DAG at scoring time (precomputed distance table refreshed on ontology updates, since the DAG changes far less often than résumés).

### 3.3 Fairness and Bias Considerations

- **Feature allowlist**: only job-relevant features (skills, experience, location/work-auth, recency) are permitted as scoring inputs. Protected/proxy attributes (name, photo, age-implying dates, gender-coded pronouns in free text, school-prestige-as-proxy-for-class) are **stripped or neutralized** during ingestion (Sec.6.2) before they ever reach the scorer — not merely down-weighted.
- **Auditable scoring**: every score is stored with its full feature vector and model version, so any decision is exactly reproducible and explainable ("why did candidate X rank #7") — this is why Sec.3.1 prefers a linear/explainable model.
- **Outcome monitoring, not just input scrubbing**: a fairness dashboard tracks selection-rate ratios across legally-permitted proxy cohorts over time on a rolling window and alerts Talent-Ops if a disparity threshold is crossed — this catches disparate impact that input scrubbing alone cannot.
- **Human-in-the-loop override**: recruiters can see the top-K explanation ("matched on: React (exact), 4 yrs > 3 yr requirement, semantic similarity 0.81") and can flag a ranking for review; flags feed back into calibration.
- **No fully-automated adverse action**: the system produces ranked shortlists, not accept/reject decisions — a human always makes the final call, which is both a fairness and (in many jurisdictions) a legal requirement for automated hiring tools.

---

---

## 4. Scheduling / Allocation Optimization

### 4.1 Problem Formulation

Model as a **bipartite graph** `G = (C ∪ J, E)`:
- `C` = candidates (or candidate-availability-slots), `J` = job roles (or role-slots within a team headcount).
- Edge `(c, j) ∈ E` exists iff candidate `c` satisfies all **hard constraints** of job `j` (skills, location, work-auth, availability window overlap).
- Edge weight `w(c, j)` = the fit score from Section 3.

Two variants, chosen per use case:

**(a) One-to-one optimal assignment (single hire per role)** — classic **assignment problem**, solved with the **Hungarian algorithm** (O(V³)) for exact optimality on moderate `|C|,|J|`, or **Hopcroft–Karp** (O(E√V)) for maximum-cardinality matching when a feasibility/coverage question ("can we fill all roles") matters more than weight-optimality.

**(b) Many-to-one / capacity-constrained assignment (team building, multiple hires per role, or one candidate eligible for multiple roles but takes only one)** — modeled as **min-cost max-flow**: source `s → each candidate (cap 1) → each eligible job (cap = 1, cost = -w(c,j)) → team sink node (cap = team headcount) → super-sink t`. Solve with **Successive Shortest Paths (SSP)** using Bellman-Ford/SPFA (handles negative costs from the negated weight) or **Dinic-based** min-cost-flow variants for larger graphs, matching the course's Module-4 network-flow curriculum directly.

### 4.2 Constraints

| Constraint type | Encoding |
|---|---|
| Hard skill requirements | Edge existence filter (no edge if unmet) |
| Team composition (e.g., "team needs ≥1 senior backend, ≥1 frontend, ≤3 total") | Per-team sub-capacity nodes in the flow graph, one node per (team, role-category) with its own capacity bound |
| Availability window | Edge existence filter — overlap test between candidate `availability` and job start window |
| Location / remote policy | Edge existence filter (hard) |
| Visa / work authorization | Edge existence filter (hard) — candidate `work_auth_status` must be in job's `work_auth_required` list |
| Soft preferences (e.g., preferred but not required skill) | Folded into edge weight `w(c,j)`, not a hard filter |

### 4.3 Objective Function

```
maximize  Σ_(c,j)∈M  w(c,j)
subject to:
  each candidate assigned to ≤ 1 job                     (candidate-side capacity)
  each job assigned ≤ headcount(j) candidates             (job-side capacity)
  per-team sub-role capacity constraints satisfied         (team composition)
  all edges in M satisfy hard constraints (already pre-filtered)
```

### 4.4 Stability Considerations

Where both sides have preferences and the marketplace needs a **stable** (not just optimal-weight) matching — i.e., no candidate–job pair would both prefer each other over their current assignment — use **Gale–Shapley deferred acceptance**, with candidates proposing to jobs ranked by their own fit-score-from-the-job's-perspective, and jobs holding the best offers up to their headcount. This trades a small amount of aggregate weight-optimality (vs. the pure max-weight assignment in 4.1) for a matching that is stable and strategy-proof for the proposing side, which matters in a marketplace where both employers and candidates can walk away. **Recommendation:** run max-weight assignment (4.1) as the default allocation for internal team-staffing use cases (Sec.5, where the platform is the sole decision-maker), and run Gale–Shapley for the open two-sided marketplace matching use case (candidates and employers both have agency to accept/decline).

---

---

## 5. Minimum Skill Set Calculation

### 5.1 Problem

Given a team-staffing goal — a set of required skills `S = {s_1 … s_k}` and a pool of candidates each covering a subset of `S` — find the **minimum number of candidates (or minimum-cost candidate set)** whose combined skills cover `S`, or, dually, the **minimum skill set** a single candidate/role must carry to close an existing team's coverage gap.

This is exactly the classic **Set Cover** problem (NP-hard — Module-5 of the course syllabus), so:

- **Exact solution (small instances, k ≤ ~20 skills or bounded team size)**: **bitmask DP** over the skill universe, `dp[mask] = min candidates to cover skill-subset `mask``, transitioning by trying each candidate's skill-subset as a bitmask OR — directly the course's Module-3 Bitmask-DP technique (`O(2^k · n)`).
- **Approximation (large instances)**: classic **greedy set-cover** — repeatedly pick the candidate whose *uncovered*-skill contribution is largest, weighted by cost if candidates have different cost (salary, urgency) — gives the standard `H(k) = O(ln k)` approximation guarantee (Module-5's approximation-algorithms content).
- **Weighted variant**: if minimizing headcount or payroll cost rather than just candidate count, use **weighted set cover**, same greedy structure with cost-effectiveness ratio `Δcoverage / cost` as the selection key.

### 5.2 Partial Staffing & Cascading Requirements

- **Partial staffing**: if full coverage of `S` is infeasible with the current pool, the algorithm falls back to **maximum-coverage-under-a-budget** (a matroid/greedy submodular-maximization variant of set cover — same greedy loop, but terminate at `budget` candidates instead of "cover everything"), reporting the residual uncovered skill set explicitly so Talent-Ops can source externally or retrain existing staff.
- **Cascading requirements**: some skills have prerequisite chains in the ontology (e.g., "Kubernetes" implicitly benefits from "Docker" + "Networking basics"). When computing minimum coverage, the DP/greedy uses the ontology-propagated skill credit from Section 2.3/3.2 — so a candidate with the parent skill contributes partial (discounted) coverage toward a child requirement, and the algorithm prefers combinations that fully cover cascading chains over combinations that leave a chain half-satisfied (implemented as a coverage-completeness bonus term in the greedy's selection key, not a hard rule, to avoid infeasibility).

---

---

## 6. Data Pipeline and Indexing

### 6.1 Ingestion

Sources: uploaded résumé files (PDF/DOCX/text), employer-submitted job postings (structured form + free text), third-party feeds (optional, via connector).

Pipeline stages: `raw upload → text extraction → language detection → field extraction (NER-style: name/contact/skills/dates) → skill normalization (Sec.2.2) → embedding generation → dedup (6.3) → index write (6.4/6.5) → ready-for-query`.

### 6.2 Cleaning & Enrichment

- Strip/hash PII per Section 8 before it reaches any downstream index that isn't access-controlled at the field level.
- Normalize date formats, unify seniority-level taxonomy, resolve company-name variants (a smaller version of the same trie/fuzzy/embedding cascade from Sec.2.2, applied to org names).
- Enrichment: infer `years_experience` per skill from date ranges in `experience[]` when not explicitly stated; infer likely seniority from title + years.

### 6.3 Deduplication

- **Exact dedup**: content hash (e.g., SHA-256 of normalized text) catches identical re-uploads.
- **Near-dup detection**: MinHash / shingling over the résumé's normalized skill-and-experience text, with a rolling hash (Rabin–Karp construction) for shingle generation and a locality-sensitive-hashing (LSH) bucket structure to avoid O(n²) pairwise comparison at millions-of-records scale — group into LSH buckets, only compare within-bucket pairs, merge/flag near-duplicate profiles (e.g., same candidate re-applying with a slightly edited résumé) above a similarity threshold.

### 6.4 Real-time vs. Batch

| Path | Trigger | Latency target | Work done |
|---|---|---|---|
| Streaming (near-real-time) | New résumé upload / new job posted | < 5 min to be queryable | Parse → normalize → embed → incremental index insert (append-only postings-list update; no full rebuild) |
| Batch (nightly / hourly) | Scheduled | Complete by next business day | Re-embedding after model updates, ontology-propagation table rebuild, dedup sweep, full index compaction/rebalancing, allocation-optimization batch run (Sec.4) for scheduled hiring cycles |

### 6.5 Caching, Sharding, Replication

- **Caching**: hot-job-posting → top-candidate-list results cached with a short TTL (minutes), invalidated on new-résumé-ingest events affecting that job's skill set (via a skill→job reverse index so we only invalidate affected caches, not everything).
- **Sharding**: inverted index and embedding index sharded by a **skill-hash range** (so a query for a given required-skill set touches a bounded number of shards) with a **résumé-ID hash** secondary sharding for the raw document store, replicated across ≥3 nodes for availability.
- **Replication**: read replicas for the query-serving path (scoring/retrieval is read-heavy); writes go through a single-leader path per shard with async replication to read replicas, acceptable given eventual consistency is fine for "résumé searchable within 5 minutes" (Sec 6.4).
- **Hand-built vs. vetted-library boundary**: per the course constraint, the *core algorithmic engine* (inverted index construction/query, string matching, DP, flow, set-cover, hashing) must be hand-built with no `java.util.*`-equivalent standard collections. Infrastructure-layer concerns that are not the pedagogical target of the course — the underlying key-value storage engine, network/replication protocol, TLS — are appropriately delegated to vetted infrastructure (a document/graph DB, a message queue), matching the course's own framing ("java.util.* forbidden **inside the engine**" — i.e., the algorithmic core, not the surrounding platform).

---

---

## 7. API and Service Contracts

### 7.1 Core Endpoints

```
POST   /v1/resumes                     — upload/create a résumé (multipart or JSON)
GET    /v1/resumes/{resume_id}         — fetch parsed résumé (access-controlled)
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
- **AuthZ**: role-based — candidates can only read/write their own résumé; employers can only read matches for their own postings and never see another employer's raw candidate pool directly (only ranked results for their job); admins have ontology-curation and audit-log access.
- **Rate limits**: per-API-key token bucket, e.g. 100 req/min for `/matches` endpoints, 10 req/min for `/allocations/run` (expensive batch op — also queued, not synchronous, above a size threshold).

### 7.4 Observability

- **Logging**: structured JSON logs per request including `request_id`, `model_version`, `latency_ms`, `caller_role`; scoring calls additionally log the full feature vector (Sec.3/8) to a write-once audit store.
- **Metrics**: latency histograms (p50/p95/p99) per endpoint, index query QPS, cache hit ratio, allocation-batch runtime, fairness-parity metrics (Sec.3.3) on a rolling dashboard.
- **Tracing**: distributed tracing (span per pipeline stage: retrieval → scoring → response) with a trace ID propagated end-to-end, so a slow match query can be attributed to a specific stage (e.g., embedding ANN lookup vs. inverted-index intersection).

---

---

## 8. Security, Privacy, and Compliance

### 8.1 Data Retention

- Résumé PII retained only as long as the candidate's consent window (default configurable, e.g., 12 months of inactivity → auto-purge or re-consent prompt).
- Audit/scoring logs (feature vectors, not raw PII) retained longer (e.g., 24 months) for compliance/explainability, since they are the record of *why* a decision was made, but are stored separately from directly-identifying fields and linked only via a rotating pseudonymous ID.

### 8.2 Access Control

- Field-level access control on `Resume.contact` (hashed/tokenized fields, decrypt-on-read only for authorized roles with a logged access event).
- Principle of least privilege: the Matching/Scoring service reads normalized skill/experience features, never raw contact PII; only the Ingestion service and candidate-facing profile endpoints touch raw PII.

### 8.3 Anonymization

- Contact fields hashed (Sec.2.1); free-text fields run through a PII-redaction pass (name/email/phone pattern stripping, plus the protected-attribute stripping from Sec.3.3) before being used as scoring/embedding input.
- Where feasible, scoring runs on a **de-identified feature vector**, so the scoring service itself never needs raw PII in memory.

### 8.4 Consent

- `ConsentRecord { given_at, scope[], revocable_until, marketing_opt_in }` stored per candidate; every processing step (matching, sharing with a specific employer, allocation) checks the relevant consent scope before proceeding; revocation triggers a purge/anonymize job.

### 8.5 DSA-3 Syllabus Alignment (course-specific note)

This system is designed so its **core algorithmic engine** maps directly onto the DSA-3 modules, satisfying the course's project-evaluation rubric while remaining a coherent production system:

| DSA-3 Module | System component using it |
|---|---|
| Module-2 (String Algorithms) | Résumé/JD text field extraction & fuzzy skill-token matching (KMP/Z/Rabin-Karp), skill-alias trie + Aho-Corasick multi-skill extraction |
| Module-3 (Advanced DP) | Wagner–Fischer edit distance for fuzzy skill/company normalization; bitmask DP for minimum skill-set (Sec.5) |
| Module-4 (Network Flow) | Min-cost max-flow allocation/assignment engine (Sec.4) |
| Module-5 (NP-Completeness & Approximation) | Set-cover formulation + greedy approximation for minimum skill set (Sec.5); assignment problem framed as an optimization/complexity discussion |
| Module-6 (Randomized & Parallel) | LSH/MinHash dedup (Sec.6.3), reservoir sampling for streaming candidate-pool sampling in dashboards, parallel prefix-sum for batch feature aggregation, Miller–Rabin-class hashing discipline for the rolling-hash shingle/dedup layer |

---

---

## 9. Deployment Architecture

### 9.1 Tech Stack Recommendation

- **Core engine language**: a systems/general-purpose language with manual data-structure control (e.g., Java or C++/Go) to honor the "hand-build every structure" constraint cleanly — no reliance on `java.util.*`/`std::` containers inside the engine module; a thin, separately-audited infra layer may use the standard library.
- **Document/graph storage**: a document DB for `Resume`/`JobPosting` (e.g., MongoDB-class), a graph DB for the Skill Ontology (e.g., Neo4j-class) — infra layer, not the algorithmic core.
- **Message queue**: for the streaming ingestion path (Kafka-class).
- **API layer**: REST (Section 7) behind an API gateway; internal services communicate over gRPC for low-latency scoring calls.
- **Frontend**: standard SPA framework for recruiter/candidate dashboards (out of scope for the algorithmic engine).

### 9.2 Deployment Model

- Containerized microservices (one container image per module in Sec.1.5), orchestrated via Kubernetes.
- Environments: `dev → staging → prod`, with staging running against a sampled/anonymized production-shaped dataset for realistic load testing.

### 9.3 CI/CD

- Every merge: unit tests (algorithm correctness — e.g., known-answer tests for KMP/edit-distance/Hungarian/set-cover against textbook examples) + integration tests (end-to-end ingest→match→allocate on a fixture dataset) + fairness-regression tests (Sec.3.3 parity check on a fixed eval set) must pass before merge.
- Canary deploys for the Scoring service (any model-weight change) with automatic rollback if fairness or latency SLOs regress.

### 9.4 Scaling Plan

- Horizontal scaling of stateless services (API gateway, Matching/Scoring) behind a load balancer.
- Index shards (Sec.6.5) scale horizontally with data volume; allocation-optimization batch jobs scale via partitioning by team/region (the flow/assignment problems are solved independently per non-overlapping candidate pool where the business logic allows it, to keep each solve tractable).

---

---

## 10. Operational Considerations

### 10.1 Monitoring & SLAs

| SLA | Target |
|---|---|
| Match query latency | p95 < 200ms |
| Résumé/job searchable after ingest | < 5 min (streaming path) |
| Allocation batch (≤100k candidate–job pairs) | < 60s |
| System availability | 99.9% monthly |
| Fairness-parity check | run continuously, alert within 1 hour of threshold breach |

### 10.2 Test Plans

- **Unit**: every hand-built algorithm (inverted index, trie, KMP/Z/Rabin-Karp, Wagner-Fischer, Hungarian/Hopcroft-Karp, min-cost-flow, bitmask-DP set cover, greedy set cover, MinHash/LSH) has a dedicated test suite against known textbook results and adversarial edge cases (empty input, single element, all-identical, worst-case-collision hash inputs).
- **Integration**: golden-path fixture (sample résumés + jobs from Sec.11) run end-to-end nightly, diffed against expected ranked output.
- **Load**: synthetic millions-of-record dataset used to validate the p95/p99 latency SLOs before each major release.
- **Fairness/regression**: a held-out labeled eval set checked on every model/weight change (Sec.9.3).

### 10.3 Migration Strategies

- Ontology changes (skill merges/splits) run through a **versioned migration script** that re-maps affected `canonical_skill_id`s across `Resume`, `JobPosting`, and the propagation-distance table, with a dry-run diff report reviewed before applying to production.
- Index-schema changes use a **dual-write + backfill + cutover** pattern (write to both old and new index during migration, backfill history, switch reads once backfill completes, decommission old index) to avoid downtime.

---

---

## 11. Example Data Schemas, Workflows, and Pseudo-code

### 11.1 Sample Résumé (abbreviated)

```json
{
  "resume_id": "r_001",
  "candidate_id": "c_001",
  "summary_text": "Backend engineer, 4 years, distributed systems.",
  "skills": [
    {"raw_text": "ReactJS", "canonical_skill_id": "skill:react_js", "confidence": 1.0, "years_experience": 4},
    {"raw_text": "postgres", "canonical_skill_id": "skill:postgresql", "confidence": 1.0, "years_experience": 3}
  ],
  "availability": {"earliest_start_date": "2026-09-01", "remote_ok": true, "work_auth_status": "OPT_EAD"}
}
```

### 11.2 Sample Job Posting (abbreviated)

```json
{
  "job_id": "j_001",
  "required_skills": [
    {"canonical_skill_id": "skill:react_js", "min_years": 3, "weight": 0.6, "hard_constraint": true},
    {"canonical_skill_id": "skill:graphql", "min_years": 1, "weight": 0.4, "hard_constraint": false}
  ],
  "work_auth_required": ["US_CITIZEN", "OPT_EAD", "H1B_OK"]
}
```

### 11.3 Skill Normalization Mapping (excerpt)

```
"reactjs" | "react.js" | "react js" | "react"  -> skill:react_js
"postgres" | "postgre sql" | "psql"             -> skill:postgresql
"k8s"                                           -> skill:kubernetes
```

### 11.4 Core Pseudocode

**(a) Skill normalization cascade (Sec.2.2)**

```
function normalize_skill(raw_token, alias_trie, ontology_embeddings, threshold_edit, threshold_cos):
    key = strip_and_lowercase(raw_token)

    // Tier 1: exact trie lookup, O(len(key))
    node = alias_trie.exact_lookup(key)
    if node is not null:
        return (node.skill_id, confidence=1.0, tier=1)

    // Tier 2: bounded fuzzy match via hand-built Wagner-Fischer edit distance
    best = null
    for candidate_alias, skill_id in alias_trie.all_entries_within_length_window(key):
        d = edit_distance(key, candidate_alias)         // Wagner-Fischer DP, O(len1*len2)
        if d <= threshold_edit(len(key)) and (best is null or d < best.distance):
            best = {skill_id, distance: d}
    if best is not null:
        confidence = 1.0 - best.distance / max(len(key), 1)
        return (best.skill_id, confidence, tier=2)

    // Tier 3: semantic embedding nearest neighbor
    vec = embed(key)
    nearest, cos_sim = ontology_embeddings.nearest_neighbor(vec)   // ANN index lookup
    if cos_sim >= threshold_cos:
        return (nearest.skill_id, confidence=cos_sim, tier=3)

    // No confident match: route to human curation queue
    enqueue_for_curation(raw_token)
    return (null, confidence=0.0, tier=none)
```

**(b) Wagner–Fischer edit distance (hand-built DP, Sec.2.2/3.2/6.2)**

```
function edit_distance(a, b):
    n, m = length(a), length(b)
    dp = new (n+1) x (m+1) matrix
    for i in 0..n: dp[i][0] = i
    for j in 0..m: dp[0][j] = j
    for i in 1..n:
        for j in 1..m:
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j]   + 1,     // deletion
                dp[i][j-1]   + 1,     // insertion
                dp[i-1][j-1] + cost   // substitution
            )
    return dp[n][m]
```

**(c) Fit score with ontology propagation (Sec.3.1/3.2)**

```
function fit_score(candidate, job, ontology_distance_table, weights):
    hard_total, hard_covered = 0, 0
    soft_total, soft_covered = 0, 0
    matched = []

    for req in job.required_skills:
        w = req.weight
        target = hard_total if req.hard_constraint else soft_total
        target += w

        best_credit = 0
        for mention in candidate.skills:
            dist = ontology_distance_table.lookup(mention.canonical_skill_id, req.canonical_skill_id)
            credit = propagation_credit(dist)         // 1.0 exact, 0.6 parent, 0.3 sibling, 0 unrelated
            if mention.years_experience is not null and req.min_years is not null:
                credit *= min(1.0, mention.years_experience / req.min_years)
            best_credit = max(best_credit, credit)

        if req.hard_constraint:
            hard_covered += w * best_credit
            if best_credit == 0: return 0.0            // hard fail: filtered out entirely
        else:
            soft_covered += w * best_credit

        if best_credit > 0:
            matched.append({skill: req.canonical_skill_id, credit: best_credit})

    hard_skill_coverage = hard_covered / max(hard_total, 1)
    soft_skill_coverage = soft_covered / max(soft_total, 1)
    semantic_similarity = cosine(candidate.embedding_vector, job.embedding_vector)
    seniority_alignment = seniority_penalty(candidate, job)
    location_fit = 1.0                                  // already hard-filtered upstream
    historical_signal = lookup_historical_acceptance(candidate.profile_cluster, job.profile_cluster)
    recency = recency_score(candidate.parsed_at)

    score = weights.hard * hard_skill_coverage
          + weights.soft * soft_skill_coverage
          + weights.depth * skill_depth_bonus(matched)
          + weights.semantic * semantic_similarity
          + weights.seniority * seniority_alignment
          + weights.location * location_fit
          + weights.historical * historical_signal
          + weights.recency * recency

    return (score, explanation={hard_skill_coverage, soft_skill_coverage, matched, semantic_similarity})
```

**(d) Min-cost max-flow allocation (Sec.4.1b)**

```
function allocate_min_cost_flow(candidates, jobs, teams, fit_scores):
    graph = new FlowGraph()
    source, sink = graph.add_node("S"), graph.add_node("T")

    for c in candidates:
        graph.add_edge(source, c.node, capacity=1, cost=0)

    for j in jobs:
        team_node = graph.get_or_create_team_subcap_node(j.team_id, j.role_category)
        for c in candidates_eligible_for(j):                 // pre-filtered by hard constraints
            cost = -fit_scores[(c, j)]                        // negate: min-cost solver maximizes weight
            graph.add_edge(c.node, j.node, capacity=1, cost=cost)
        graph.add_edge(j.node, team_node, capacity=j.headcount, cost=0)

    for team_node in graph.team_subcap_nodes:
        graph.add_edge(team_node, sink, capacity=team_node.role_category_cap, cost=0)

    result = successive_shortest_paths_min_cost_flow(graph, source, sink)   // Bellman-Ford/SPFA based
    return extract_assignment_pairs(result)
```

**(e) Bitmask DP minimum skill-set / team cover (Sec.5.1, exact for small k)**

```
function min_candidates_to_cover(skills_universe, candidate_skill_masks):
    // skills_universe: list of k skills -> bit positions 0..k-1
    // candidate_skill_masks[i]: bitmask of skills candidate i covers
    n = length(candidate_skill_masks)
    FULL = (1 << k) - 1
    dp = array of size (1 << k), initialized to INF
    choice = array of size (1 << k), initialized to -1
    dp[0] = 0

    for mask in 0 .. FULL:
        if dp[mask] == INF: continue
        for i in 0 .. n-1:
            new_mask = mask | candidate_skill_masks[i]
            if dp[mask] + 1 < dp[new_mask]:
                dp[new_mask] = dp[mask] + 1
                choice[new_mask] = (mask, i)

    if dp[FULL] == INF: return "infeasible: no combination covers all required skills"
    return reconstruct_candidate_set(choice, FULL)
```

**(f) Greedy weighted set cover (Sec.5.1, approximation for large k/n)**

```
function greedy_set_cover(skills_universe, candidates, cost_fn):
    uncovered = set(skills_universe)
    chosen = []
    while uncovered is not empty:
        best_candidate, best_ratio = null, -infinity
        for c in candidates not in chosen:
            new_coverage = size(intersection(c.skills, uncovered))
            if new_coverage == 0: continue
            ratio = new_coverage / cost_fn(c)          // cost-effectiveness
            if ratio > best_ratio:
                best_ratio, best_candidate = ratio, c
        if best_candidate is null:
            return {chosen, residual_uncovered: uncovered}   // partial staffing (Sec.5.2)
        chosen.append(best_candidate)
        uncovered -= best_candidate.skills
    return {chosen, residual_uncovered: {}}
```

### 11.5 End-to-End Workflow (new job posting → shortlist)

```
1. Employer submits JobPosting -> Ingestion Service
2. Skill Normalizer resolves required/preferred skills to canonical IDs (11.4a)
3. Job embedded (embedding_vector) and written to Job Store + Inverted Index (Sec.6.4 streaming path)
4. Recruiter calls GET /v1/jobs/{id}/matches
5. Matching Service: Stage A retrieval (inverted index + hard filters) -> top-N candidate set
6. Matching Service: Stage B scoring (11.4c) over top-N -> ranked list with explanations
7. Response cached (Sec.6.5) with skill-based invalidation key
8. If team-staffing mode: recruiter calls POST /v1/allocations/run -> min-cost-flow (11.4d)
9. If gap identified: POST /v1/teams/{id}/min-skill-set -> bitmask DP or greedy set cover (11.4e/f)
10. All scoring/allocation decisions logged to audit store (Sec.7.4/8.1) with feature vectors
```

---

---

## 12. Documentation Artifacts

### 12.1 API Reference

See Section 7 for the endpoint contracts; a full OpenAPI/Swagger spec should be generated from the same source-of-truth schema definitions in Section 2 and 7 to prevent drift, and published alongside each release.

### 12.2 Data Dictionary

| Field | Type | Description | PII? |
|---|---|---|---|
| `resume_id` | UUID | Internal résumé identifier | No |
| `candidate_id` | UUID | Internal candidate identifier | No |
| `contact.email_hash` | string | Salted hash of email | Sensitive (hashed) |
| `skills[].canonical_skill_id` | string | Ontology-normalized skill ID | No |
| `skills[].confidence` | float [0,1] | Normalization confidence | No |
| `job_id` | UUID | Internal job identifier | No |
| `required_skills[].hard_constraint` | bool | Whether absence filters the candidate out entirely | No |
| `embedding_vector` | float[d] | Dense semantic embedding | No (derived, non-reversible in practice but treated with same care as source text) |
| `ConsentRecord.scope[]` | string[] | Purposes candidate has consented to | Governance-sensitive |

### 12.3 Glossary

- **Canonical skill ID** — the single, ontology-stable identifier a raw skill string is normalized to.
- **Hard constraint** — a requirement that, if unmet, excludes a candidate from consideration entirely (as opposed to lowering their score).
- **Ontology propagation** — crediting a candidate for a related (parent/sibling/child) skill at a discounted weight, rather than requiring an exact string match.
- **Stable matching** — an assignment where no unmatched candidate–job pair would both prefer switching to each other over their current assignment.
- **Set cover** — the NP-hard problem of selecting the minimum number of sets (here, candidates) whose union covers a target universe (here, required skills).
- **Min-cost max-flow** — a network-flow formulation that finds the maximum-flow assignment of least total cost, used here to solve capacity-constrained team staffing.

### 12.4 User Guides (outline)

- **Recruiter Quick Start**: post a job → view ranked matches → read match explanations → shortlist/reject → (optional) run team allocation.
- **Candidate Quick Start**: upload résumé → review parsed/normalized skills → set availability/consent → view job matches.
- **Admin Guide**: curate the skill ontology (merge aliases, add nodes), review the fairness dashboard, manage consent/retention exceptions.

### 12.5 Developer Onboarding Notes

- Read Sections 1–2 first (architecture + data model) before touching any service code.
- The algorithmic core (Sec.11.4) must remain free of standard-library collection/algorithm calls — see Sec.6.5's hand-built-vs-infra boundary before adding any dependency.
- Every new/changed scoring feature requires: (1) a unit test with a known-answer fixture, (2) a fairness-regression run (Sec.9.3/10.2), (3) an update to the Data Dictionary (Sec.12.2) and API reference if it appears in `explanation`.
- Local dev environment: run the fixture dataset from Sec.11.1–11.2 through the full pipeline (Sec.11.5) as the first smoke test.

---

---

## 13. Phasing: MVP → Enhancements

### Phase 0 — MVP (Weeks 1–4)

**Goal:** end-to-end single-machine pipeline proving the core algorithms, sized for course-project demo scale (hundreds–thousands of records), directly exercising DSA-3 Modules 2–5.

Deliverables:
- Hand-built inverted index + trie-based skill alias dictionary (Sec.2.4/6).
- Skill normalization tiers 1–2 (exact + edit-distance fuzzy); tier 3 (embeddings) stubbed/optional.
- Linear fit-scoring model (Sec.3.1) without historical-signal feature (no data yet to learn it from).
- One-to-one Hungarian-algorithm assignment (Sec.4.1a) for a single-role-per-hire demo.
- Bitmask-DP exact minimum-skill-set solver (Sec.5.1) for small teams.
- Minimal REST API (`POST /resumes`, `POST /jobs`, `GET /jobs/{id}/matches`).
- Unit tests for every hand-built algorithm against textbook known-answers.

### Phase 1 — Core Product (Weeks 5–8)

**Goal:** multi-role allocation, approximate algorithms for scale, first pass at fairness/audit.

Deliverables:
- Min-cost max-flow allocation engine with team-composition constraints (Sec.4.1b/4.2).
- Greedy set-cover approximation + partial-staffing fallback (Sec.5.2).
- Ontology DAG with propagation-credit scoring (Sec.2.3/3.2).
- Audit logging of every scored decision with feature vectors (Sec.7.4/8.1).
- Streaming ingestion path for near-real-time indexing (Sec.6.4).

### Phase 2 — Scale & Fairness Hardening (Weeks 9–12)

**Goal:** millions-of-record readiness and compliance maturity.

Deliverables:
- Embedding tier-3 normalization + ANN semantic search (Sec.2.2/6.4).
- Sharding/replication of indexes (Sec.6.5), caching layer with skill-based invalidation.
- MinHash/LSH deduplication at scale (Sec.6.3).
- Fairness-parity monitoring dashboard + calibrated-weight retraining pipeline (Sec.3.3/9.3).
- Gale–Shapley stable-matching mode for the open two-sided marketplace (Sec.4.4).
- Consent/retention automation and PII field-level access control (Sec.8).
- Full observability stack: tracing, SLO dashboards, canary deploys (Sec.7.4/9.3/10.1).

### Phase 3 — Continuous Enhancement (ongoing)

- Monthly scoring-model recalibration; quarterly ontology-curation review.
- A/B testing of scoring-weight changes behind the canary pipeline.
- Parallel-algorithm optimizations (Module-6: parallel prefix-sum for feature aggregation, parallel sort for large ranking batches) as data volume grows past single-node throughput.
- Migration tooling maturity (Sec.10.3) exercised on real ontology-evolution events.

---

*End of document.*

---

*End of document.*
