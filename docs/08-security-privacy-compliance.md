## 8. Security, Privacy, and Compliance

### 8.1 Data Retention

- Resume PII retained only as long as the candidate's consent window (default configurable, e.g., 12 months of inactivity → auto-purge or re-consent prompt).
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
| Module-2 (String Algorithms) | Resume/JD text field extraction & fuzzy skill-token matching (KMP/Z/Rabin-Karp), skill-alias trie + Aho-Corasick multi-skill extraction |
| Module-3 (Advanced DP) | Wagner–Fischer edit distance for fuzzy skill/company normalization; bitmask DP for minimum skill-set (Sec.5) |
| Module-4 (Network Flow) | Min-cost max-flow allocation/assignment engine (Sec.4) |
| Module-5 (NP-Completeness & Approximation) | Set-cover formulation + greedy approximation for minimum skill set (Sec.5); assignment problem framed as an optimization/complexity discussion |
| Module-6 (Randomized & Parallel) | LSH/MinHash dedup (Sec.6.3), reservoir sampling for streaming candidate-pool sampling in dashboards, parallel prefix-sum for batch feature aggregation, Miller–Rabin-class hashing discipline for the rolling-hash shingle/dedup layer |

---

