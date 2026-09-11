## 12. Documentation Artifacts

### 12.1 API Reference

See Section 7 for the endpoint contracts; a full OpenAPI/Swagger spec should be generated from the same source-of-truth schema definitions in Section 2 and 7 to prevent drift, and published alongside each release.

### 12.2 Data Dictionary

| Field | Type | Description | PII? |
|---|---|---|---|
| `resume_id` | UUID | Internal resume identifier | No |
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
- **Candidate Quick Start**: upload resume → review parsed/normalized skills → set availability/consent → view job matches.
- **Admin Guide**: curate the skill ontology (merge aliases, add nodes), review the fairness dashboard, manage consent/retention exceptions.

### 12.5 Developer Onboarding Notes

- Read Sections 1–2 first (architecture + data model) before touching any service code.
- The algorithmic core (Sec.11.4) must remain free of standard-library collection/algorithm calls — see Sec.6.5's hand-built-vs-infra boundary before adding any dependency.
- Every new/changed scoring feature requires: (1) a unit test with a known-answer fixture, (2) a fairness-regression run (Sec.9.3/10.2), (3) an update to the Data Dictionary (Sec.12.2) and API reference if it appears in `explanation`.
- Local dev environment: run the fixture dataset from Sec.11.1–11.2 through the full pipeline (Sec.11.5) as the first smoke test.

---

