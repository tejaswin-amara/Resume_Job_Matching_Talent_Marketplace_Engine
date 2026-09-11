## 10. Operational Considerations

### 10.1 Monitoring & SLAs

| SLA | Target |
|---|---|
| Match query latency | p95 < 200ms |
| Resume/job searchable after ingest | < 5 min (streaming path) |
| Allocation batch (≤100k candidate–job pairs) | < 60s |
| System availability | 99.9% monthly |
| Fairness-parity check | run continuously, alert within 1 hour of threshold breach |

### 10.2 Test Plans

- **Unit**: every hand-built algorithm (inverted index, trie, KMP/Z/Rabin-Karp, Wagner-Fischer, Hungarian/Hopcroft-Karp, min-cost-flow, bitmask-DP set cover, greedy set cover, MinHash/LSH) has a dedicated test suite against known textbook results and adversarial edge cases (empty input, single element, all-identical, worst-case-collision hash inputs).
- **Integration**: golden-path fixture (sample resumes + jobs from Sec.11) run end-to-end nightly, diffed against expected ranked output.
- **Load**: synthetic millions-of-record dataset used to validate the p95/p99 latency SLOs before each major release.
- **Fairness/regression**: a held-out labeled eval set checked on every model/weight change (Sec.9.3).

### 10.3 Migration Strategies

- Ontology changes (skill merges/splits) run through a **versioned migration script** that re-maps affected `canonical_skill_id`s across `Resume`, `JobPosting`, and the propagation-distance table, with a dry-run diff report reviewed before applying to production.
- Index-schema changes use a **dual-write + backfill + cutover** pattern (write to both old and new index during migration, backfill history, switch reads once backfill completes, decommission old index) to avoid downtime.

---

