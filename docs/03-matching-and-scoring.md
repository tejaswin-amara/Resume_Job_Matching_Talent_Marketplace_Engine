## 3. Matching and Scoring

### 3.1 Candidate–Job Fit Scoring Model

Two-stage architecture:

**Stage A — Retrieval (cheap, high-recall).** Inverted-index Boolean/BM25 retrieval + hard-constraint filtering (location, work-auth, hard-required skills) narrows millions of resumes to a top-N (e.g., N=2,000) candidate set per job in milliseconds.

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
| `recency` | freshness of resume data | 0.05 |

Weights are **calibrated**, not hand-guessed at production time: fit via logistic regression / gradient boosting on historical (candidate, job, employer_interview_decision) labels, then the *learned* weights are frozen into the linear explainable model above (distillation of a possibly-nonlinear model into an explainable linear one is preferred to shipping the nonlinear model directly, to preserve the auditability requirement in Sec.8). Recalibrate on a monthly cadence or when feature drift exceeds a threshold (Sec.10).

### 3.2 Handling Synonyms, Expansion, and Hierarchies in Scoring

- **Synonym expansion at query time**: a job requiring `skill:react_js` is expanded, before retrieval, to the alias set `{react, reactjs, react.js, react_native? (configurable)}` via the ontology, so the inverted-index lookup doesn't miss resumes that used a different literal string.
- **Hierarchy-aware partial credit**: `hard_skill_coverage` is not binary per skill — a candidate with a **child** of the required skill gets full credit; a candidate with the **direct parent** gets partial credit (configurable, e.g. 0.6); a **sibling** gets smaller partial credit (e.g. 0.3); unrelated gets 0. This is implemented as a shortest-path lookup on the ontology DAG at scoring time (precomputed distance table refreshed on ontology updates, since the DAG changes far less often than resumes).

### 3.3 Fairness and Bias Considerations

- **Feature allowlist**: only job-relevant features (skills, experience, location/work-auth, recency) are permitted as scoring inputs. Protected/proxy attributes (name, photo, age-implying dates, gender-coded pronouns in free text, school-prestige-as-proxy-for-class) are **stripped or neutralized** during ingestion (Sec.6.2) before they ever reach the scorer — not merely down-weighted.
- **Auditable scoring**: every score is stored with its full feature vector and model version, so any decision is exactly reproducible and explainable ("why did candidate X rank #7") — this is why Sec.3.1 prefers a linear/explainable model.
- **Outcome monitoring, not just input scrubbing**: a fairness dashboard tracks selection-rate ratios across legally-permitted proxy cohorts over time on a rolling window and alerts Talent-Ops if a disparity threshold is crossed — this catches disparate impact that input scrubbing alone cannot.
- **Human-in-the-loop override**: recruiters can see the top-K explanation ("matched on: React (exact), 4 yrs > 3 yr requirement, semantic similarity 0.81") and can flag a ranking for review; flags feed back into calibration.
- **No fully-automated adverse action**: the system produces ranked shortlists, not accept/reject decisions — a human always makes the final call, which is both a fairness and (in many jurisdictions) a legal requirement for automated hiring tools.

---

