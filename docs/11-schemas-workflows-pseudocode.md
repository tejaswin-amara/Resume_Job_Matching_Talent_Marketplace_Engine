## 11. Example Data Schemas, Workflows, and Pseudo-code

### 11.1 Sample Resume (abbreviated)

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

