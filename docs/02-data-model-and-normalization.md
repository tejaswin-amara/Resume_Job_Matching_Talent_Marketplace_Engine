## 2. Data Model & Normalization

### 2.1 Core Schemas

```jsonc
// Resume (canonical, post-parsing)
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
| Inverted index (skills → resume IDs) | Fast candidate retrieval for a required-skill set (Boolean/ranked retrieval) | Hand-built postings lists, sorted by `resume_id`, skip pointers for fast intersection (same design as classic IR inverted indexes; must be hand-built per engine constraint) |
| Inverted index (n-gram/shingle → resume IDs) | Free-text / fuzzy title & company search | Rolling-hash (Rabin–Karp style) shingling, same postings-list structure |
| Trie (skill alias dictionary) | O(len) exact + prefix skill lookup, autocomplete | Hand-built trie, Aho-Corasick automaton for multi-skill extraction from resume free text in one pass |
| Embedding ANN index | Semantic resume↔job similarity, fuzzy skill fallback | HNSW-style graph index (approximate) — see Sec.6.5 for the "hand-built vs. vetted-library" boundary decision |
| Ranking signal store | Precomputed features feeding the scorer (recency, popularity, historical acceptance rate) | Columnar feature store, updated batch + streaming |

**Ranking signals used at retrieval time** (before the full scorer runs — this is a cheap first-pass filter/rank to shrink the candidate set from millions to a few thousand before the expensive scoring model runs):
- BM25-style term frequency / inverse document frequency over the skill inverted index.
- Recency of resume update.
- Location/remote compatibility (hard filter).
- Work-authorization compatibility (hard filter).

---

