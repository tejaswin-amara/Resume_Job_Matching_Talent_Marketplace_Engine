## 6. Data Pipeline and Indexing

### 6.1 Ingestion

Sources: uploaded resume files (PDF/DOCX/text), employer-submitted job postings (structured form + free text), third-party feeds (optional, via connector).

Pipeline stages: `raw upload → text extraction → language detection → field extraction (NER-style: name/contact/skills/dates) → skill normalization (Sec.2.2) → embedding generation → dedup (6.3) → index write (6.4/6.5) → ready-for-query`.

### 6.2 Cleaning & Enrichment

- Strip/hash PII per Section 8 before it reaches any downstream index that isn't access-controlled at the field level.
- Normalize date formats, unify seniority-level taxonomy, resolve company-name variants (a smaller version of the same trie/fuzzy/embedding cascade from Sec.2.2, applied to org names).
- Enrichment: infer `years_experience` per skill from date ranges in `experience[]` when not explicitly stated; infer likely seniority from title + years.

### 6.3 Deduplication

- **Exact dedup**: content hash (e.g., SHA-256 of normalized text) catches identical re-uploads.
- **Near-dup detection**: MinHash / shingling over the resume's normalized skill-and-experience text, with a rolling hash (Rabin–Karp construction) for shingle generation and a locality-sensitive-hashing (LSH) bucket structure to avoid O(n²) pairwise comparison at millions-of-records scale — group into LSH buckets, only compare within-bucket pairs, merge/flag near-duplicate profiles (e.g., same candidate re-applying with a slightly edited resume) above a similarity threshold.

### 6.4 Real-time vs. Batch

| Path | Trigger | Latency target | Work done |
|---|---|---|---|
| Streaming (near-real-time) | New resume upload / new job posted | < 5 min to be queryable | Parse → normalize → embed → incremental index insert (append-only postings-list update; no full rebuild) |
| Batch (nightly / hourly) | Scheduled | Complete by next business day | Re-embedding after model updates, ontology-propagation table rebuild, dedup sweep, full index compaction/rebalancing, allocation-optimization batch run (Sec.4) for scheduled hiring cycles |

### 6.5 Caching, Sharding, Replication

- **Caching**: hot-job-posting → top-candidate-list results cached with a short TTL (minutes), invalidated on new-resume-ingest events affecting that job's skill set (via a skill→job reverse index so we only invalidate affected caches, not everything).
- **Sharding**: inverted index and embedding index sharded by a **skill-hash range** (so a query for a given required-skill set touches a bounded number of shards) with a **resume-ID hash** secondary sharding for the raw document store, replicated across ≥3 nodes for availability.
- **Replication**: read replicas for the query-serving path (scoring/retrieval is read-heavy); writes go through a single-leader path per shard with async replication to read replicas, acceptable given eventual consistency is fine for "resume searchable within 5 minutes" (Sec 6.4).
- **Hand-built vs. vetted-library boundary**: per the course constraint, the *core algorithmic engine* (inverted index construction/query, string matching, DP, flow, set-cover, hashing) must be hand-built with no `java.util.*`-equivalent standard collections. Infrastructure-layer concerns that are not the pedagogical target of the course — the underlying key-value storage engine, network/replication protocol, TLS — are appropriately delegated to vetted infrastructure (a document/graph DB, a message queue), matching the course's own framing ("java.util.* forbidden **inside the engine**" — i.e., the algorithmic core, not the surrounding platform).

---

