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
'''
flowchart TD
    %% Styling and Classes
    classDef client fill:#E1F5FE,stroke:#0288D1,stroke-width:2px,color:#01579B;
    classDef gateway fill:#EDE7F6,stroke:#7E57C2,stroke-width:2px,color:#4527A0;
    classDef service fill:#E8F5E9,stroke:#43A047,stroke-width:2px,color:#1B5E20;
    classDef data fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px,color:#E65100;
    classDef pipeline fill:#FCE4EC,stroke:#D81B60,stroke-width:2px,color:#880E4F;
    classDef obs fill:#ECEFF1,stroke:#607D8B,stroke-width:2px,color:#263238;

    %% Client Layer
    subgraph Client_Layer ["Client Layer"]
        UI_Candidate["Candidate Web / Mobile UI"]
        UI_Recruiter["Recruiter / Admin Portal"]
    end
    class UI_Candidate,UI_Recruiter client;

    %% API Gateway Layer
    subgraph Gateway_Layer ["API Gateway & Security Layer"]
        Gateway["API Gateway / Envoy / Kong<br/>(AuthN / AuthZ / Rate Limiting / WAF)"]
    end
    class Gateway gateway;

    %% Application Microservices Layer
    subgraph Core_Services ["Core Application Services Layer"]
        Ingestion_Svc["Ingestion Service<br/>(Parsing, Normalization & ETL)"]
        Matching_Svc["Matching & Scoring Service<br/>(Hybrid Lexical, Semantic & GNN Scoring)"]
        Allocation_Svc["Allocation & Optimization Service<br/>(Bipartite Matching, MCMF & Interview Flow)"]
    end
    class Ingestion_Svc,Matching_Svc,Allocation_Svc service;

    %% Data & Index Storage Layer
    subgraph Storage_Layer ["Core Data & Index Layer"]
        direction TB
        subgraph Doc_Stores ["Document & Relational Stores"]
            Doc_Resume[("Résumé Store<br/>(Document DB / S3 Vault)")]
            Doc_Job[("Job Store<br/>(PostgreSQL / MongoDB)")]
        end
        subgraph Search_Indexes ["Indexing Systems"]
            Inverted_Index[("Hand-Built Inverted Index<br/>(BM25 / Boolean Postings)")]
            Vector_Index[("Embedding Index<br/>(HNSW / ScaNN / FAISS)")]
            Ontology_Graph[("Skill Ontology Graph<br/>(Neo4j / Property Graph)")]
        end
        Feature_Store[("Feature Store<br/>(Redis / Versioned Feature DB)")]
    end
    class Doc_Resume,Doc_Job,Inverted_Index,Vector_Index,Ontology_Graph,Feature_Store data;

    %% Data Processing Pipelines
    subgraph Processing_Layer ["Data Processing Pipelines"]
        Streaming_Pipe["Streaming Pipeline<br/>(Kafka / Flink / CDC Event-Driven Reindexing)"]
        Batch_Pipe["Batch Pipeline<br/>(Nightly ETL, Deduplication, Model Re-Embedding)"]
    end
    class Streaming_Pipe,Batch_Pipe pipeline;

    %% Cross-Cutting Observability & Compliance
    subgraph Observability_Layer ["Cross-Cutting Observability & Governance"]
        Audit_Fairness["Fairness & Bias Audit Engine<br/>(Four-Fifths Rule, Disparate Impact Monitoring)"]
        Telemetry["Telemetry Platform<br/>(Prometheus, Grafana, OpenTelemetry Traces, Loki)"]
    end
    class Audit_Fairness,Telemetry obs;

    %% Client to Gateway
    UI_Candidate -->|REST / GraphQL| Gateway
    UI_Recruiter -->|REST / GraphQL| Gateway

    %% Gateway to Microservices
    Gateway -->|Résumé & Job Uploads| Ingestion_Svc
    Gateway -->|Search & Ranking Queries| Matching_Svc
    Gateway -->|Schedule & Slot Allocation| Allocation_Svc

    %% Ingestion Pipeline Flow
    Ingestion_Svc -->|Persist Parsed Raw Documents| Doc_Resume
    Ingestion_Svc -->|Persist Job Postings| Doc_Job
    Ingestion_Svc -->|Publish Ingestion Events| Streaming_Pipe

    %% Streaming & Batch Updates to Storage
    Streaming_Pipe -->|Update Near-Real-Time Postings| Inverted_Index
    Streaming_Pipe -->|Incremental Embeddings| Vector_Index
    Batch_Pipe -->|Full Model Sync & Embeddings| Vector_Index
    Batch_Pipe -->|Taxonomy Enrichment| Ontology_Graph
    Batch_Pipe -->|Extract Candidate & Job Signals| Feature_Store
    Doc_Resume -.->|Raw Reads| Batch_Pipe
    Doc_Job -.->|Raw Reads| Batch_Pipe

    %% Matching Service Retrievals
    Matching_Svc -->|1. Candidate Fast Filtering| Inverted_Index
    Matching_Svc -->|2. Dense Semantic Search| Vector_Index
    Matching_Svc -->|3. Skill Traversal & Synonyms| Ontology_Graph
    Matching_Svc -->|4. Feature Enrichment| Feature_Store
    Matching_Svc -->|Feed Qualified Shortlist| Allocation_Svc

    %% Allocation Execution
    Allocation_Svc -->|Read Candidate Data| Doc_Resume
    Allocation_Svc -->|Read Capacity & Deadlines| Doc_Job

    %% Observability & Governance Hooks
    Matching_Svc -.->|Audit Scores & Outputs| Audit_Fairness
    Allocation_Svc -.->|Audit Matching Allocations| Audit_Fairness
    Ingestion_Svc -.->|Metrics & Distributed Traces| Telemetry
    Matching_Svc -.->|Metrics & Distributed Traces| Telemetry
    Allocation_Svc -.->|Metrics & Distributed Traces| Telemetry
'''

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

