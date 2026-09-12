<div align="center">

# 🧭 Resume–Job Matching & Talent-Marketplace Engine

**Full-stack system design for matching millions of candidates to open roles.**

Every core algorithm—search, fuzzy matching, scoring, optimal assignment, NP-hard set cover—is built from first principles. No library shortcuts. Built as **DSA-3**, designed to ship.

[![Status](https://img.shields.io/badge/status-documentation%20v1.0-blue)](docs/01-system-overview.md)
[![Course](https://img.shields.io/badge/course-DSA--3%20(25CS2103E)-6f42c1)](docs/01-system-overview.md)
[![University](https://img.shields.io/badge/KLBCH-Odd%20Sem%202026--27-orange)](ABSTRACT/README.md)
[![Docs](https://img.shields.io/badge/docs-13%20sections-success)](docs/01-system-overview.md)
[![License](https://img.shields.io/badge/license-Academic%20Project-lightgrey)](LICENSE)
[![Team](https://img.shields.io/badge/team-36%20·%20Section%2010-informational)](ABSTRACT/README.md)

</div>

---

## The Problem

At scale, recruitment breaks. Companies with thousands of open roles and millions of candidates need automated systems to answer three hard questions:

1. **Search:** Which candidates actually fit this job?
2. **Match:** How do we assign candidates to roles under real constraints—budget, geography, skill gaps?
3. **Staff:** What's the minimal hiring set that covers all required skills?

This engine answers all three using hand-built algorithms. No black boxes. Every core routine—from inverted-index retrieval to min-cost max-flow to NP-hard set cover—is implemented from first principles.

---

## How It Works: Three Stages

```
┌─────────────────┬──────────────────┬──────────────────┐
│                 │                  │                  │
│   RETRIEVAL     │     SCORING      │   ALLOCATION     │
│                 │                  │                  │
│ Find candidates │ Rank by fit      │ Assign under     │
│ that match      │ semantically     │ constraints      │
│ the job         │ and explicitly   │ (budget, skills) │
│                 │                  │                  │
└─────────────────┴──────────────────┴──────────────────┘
```

### Stage 1: Retrieval

**Question:** Which candidates could fit this job?

- Build an **inverted index** of candidate skills and attributes
- Use **Aho-Corasick** for fast multi-pattern skill matching
- Return ranked candidate list in milliseconds

### Stage 2: Scoring

**Question:** Which candidates fit *best*?

- **Fuzzy matching:** Handle typos, abbreviations, synonyms (edit distance, prefix matching)
- **Semantic fallback:** When exact matches fail, use vector embeddings + ANN index
- **Explainable scoring:** Weighted sum of fit signals (skill match %, years of experience, location proximity, etc.)

### Stage 3: Allocation

**Question:** How do we assign candidates to roles fairly under constraints?

- **One-to-one matching:** Hungarian algorithm or Hopcroft–Karp
- **One-to-many or many-to-many:** Min-cost max-flow network
- **Two-sided marketplaces:** Gale–Shapley deferred acceptance (stable matching)

**Bonus: Team Staffing**

Need to hire a team covering all required skills? Use:
- **Small teams:** Exact solution via bitmask dynamic programming
- **Large hiring sprees:** Greedy set-cover approximation (O(ln k) optimal)

### The Data Foundation

Before retrieval, normalize everything:

- **Resumes & jobs** → structured skill profiles (not text blobs)
- **Skill resolution:** "JS" = "JavaScript" = "javascript.ts" (ontology graph + dedup)
- **Alias handling:** "Python 3.x" matches "Python"
- **Standardized schemas:** See [`docs/02-data-model-and-normalization.md`](docs/02-data-model-and-normalization.md)

---

## Documentation: 13 Sections

**13 engineering sections** covering every layer: architecture, algorithms, data pipelines, APIs, security, deployment, and phased rollout. Every section includes pseudocode, workflows, and decision rationale.

### Getting Oriented

| Section | What's inside |
|---------|---|
| **1** — [System Overview](docs/01-system-overview.md) | High-level architecture, stakeholders, success metrics, module responsibilities |
| **2** — [Data Model & Normalization](docs/02-data-model-and-normalization.md) | Resume/job schemas, skill resolution, ontology graph design |

### The Three Core Algorithms

| Section | What's inside |
|---------|---|
| **3** — [Matching & Scoring](docs/03-matching-and-scoring.md) | Fit-scoring models, fuzzy matching, semantic fallback, fairness & bias |
| **4** — [Scheduling & Allocation](docs/04-scheduling-and-allocation.md) | Assignment problem formulations, constraints, stable matching |
| **5** — [Minimum Skill Set](docs/05-minimum-skill-set.md) | Set-cover formulation, exact DP, greedy approximation, O(ln k) guarantee |

### Building & Operating

| Section | What's inside |
|---------|---|
| **6** — [Data Pipeline & Indexing](docs/06-data-pipeline-and-indexing.md) | Ingestion, dedup, real-time vs. batch, sharding, index maintenance |
| **7** — [API & Service Contracts](docs/07-api-and-service-contracts.md) | Endpoint specs, request/response schemas, auth, rate limiting, observability |
| **8** — [Security, Privacy & Compliance](docs/08-security-privacy-compliance.md) | Data retention, access control, consent, legal, DSA-3 alignment |
| **9** — [Deployment Architecture](docs/09-deployment-architecture.md) | Tech stack, containerization, CI/CD, horizontal scaling strategy |
| **10** — [Operational Considerations](docs/10-operational-considerations.md) | Test plans, SLAs, migrations, runbooks, incident response |

### Reference & Implementation

| Section | What's inside |
|---------|---|
| **11** — [Schemas, Workflows & Pseudocode](docs/11-schemas-workflows-pseudocode.md) | **Runnable pseudocode for every algorithm** — transcribe directly into your code |
| **12** — [Documentation Artifacts](docs/12-documentation-artifacts.md) | API reference, data dictionary, glossary, decision log |
| **13** — [Phasing: MVP → Enhancements](docs/13-phasing-roadmap.md) | Timeline, per-phase deliverables, success criteria, scope per release |

**Single-file version:** [`FULL-DOCUMENTATION.md`](FULL-DOCUMENTATION.md) (auto-generated, kept in sync by CI, never hand-edited)

---

## System Architecture

Three independent microservices, one data layer, scales horizontally.

```
                          ┌─────────────────────┐
                          │   Client Layer      │
                          │  (Web / Mobile UI)  │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │   API Gateway       │
                          │  (Auth, Rate Limit) │
                          └─┬──────────┬────┬───┘
                            │          │    │
                ┌───────────┴┐   ┌─────┴──┐ │
                │             │   │        │ │
           ┌────▼────────┐ ┌─▼───▼─────┐ ┌┴─▼────────┐
           │ Ingestion & │ │ Matching  │ │Allocation │
           │    ETL      │ │ & Scoring │ │ & Optimize│
           └────┬────────┘ └─┬───────┬─┘ └─┬─────────┘
                │            │       │     │
                └────────────┴───┬───┴─────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   Storage & Index Layer   │
                    ├──────────────────────────┤
                    │ • Resume/Job documents   │
                    │ • Inverted indexes       │
                    │ • Vector ANN indexes     │
                    │ • Skill ontology graph   │
                    └──────────────────────────┘
```

Each service scales independently. See [`docs/01-system-overview.md`](docs/01-system-overview.md) for the full architecture and module breakdown.

---

## Core Algorithms: Hand-Built from First Principles

No `java.util.*` shortcuts. No off-the-shelf matching libraries. Every algorithm is implemented from scratch:

| Problem | Algorithm | Reference |
|---------|-----------|-----------|
| Exact/fuzzy skill matching | Trie + Aho-Corasick, Wagner-Fischer edit distance | [`03-matching-and-scoring.md`](docs/03-matching-and-scoring.md) |
| Semantic fallback matching | Cosine similarity + ANN index (vector embeddings) | [`03-matching-and-scoring.md`](docs/03-matching-and-scoring.md) |
| Candidate retrieval at scale | Hand-built inverted index with skip pointers | [`06-data-pipeline-and-indexing.md`](docs/06-data-pipeline-and-indexing.md) |
| Candidate ↔ job assignment | Hungarian / Hopcroft–Karp / min-cost max-flow | [`04-scheduling-and-allocation.md`](docs/04-scheduling-and-allocation.md) |
| Two-sided marketplace | Gale–Shapley deferred acceptance (stable matching) | [`04-scheduling-and-allocation.md`](docs/04-scheduling-and-allocation.md) |
| Minimum team skill set | Bitmask DP (exact) · Greedy set cover (O(ln k)) | [`05-minimum-skill-set.md`](docs/05-minimum-skill-set.md) |
| Near-duplicate detection | Rolling-hash shingling + MinHash/LSH | [`06-data-pipeline-and-indexing.md`](docs/06-data-pipeline-and-indexing.md) |

**Pseudocode for every algorithm** is in [`docs/11-schemas-workflows-pseudocode.md`](docs/11-schemas-workflows-pseudocode.md). Transcribe directly into your code.

---

## DSA-3 Syllabus → Implementation

The system **is** the course. Every algorithm traces directly back to the **DSA-3 (25CS2103E)** module:

| Module | Topic | How we use it | Reference |
|--------|-------|---|---|
| **2** | String Algorithms | KMP, Z-algorithm, Rabin-Karp, Aho-Corasick → fast skill extraction | `03-matching-and-scoring.md` |
| **3** | Advanced DP | Wagner–Fischer (skill edit distance) + Bitmask DP (team coverage) | `05-minimum-skill-set.md` |
| **4** | Network Flow | Min-cost max-flow → optimal candidate ↔ role allocation | `04-scheduling-and-allocation.md` |
| **5** | NP & Approximation | Set-cover formulation + greedy approx (O(ln k) guarantee) | `05-minimum-skill-set.md` |
| **6** | Randomized & Parallel | MinHash/LSH (dedup), reservoir sampling, parallel prefix-sum | `06-data-pipeline-and-indexing.md` |

This project *implements* the DSA-3 syllabus. See [`docs/08-security-privacy-compliance.md §8.5`](docs/08-security-privacy-compliance.md) for full alignment notes.

---

## Status & Timeline

| Phase | What you build | Current state |
|-------|---|---|
| **Phase 0** | Single-machine MVP, core algorithms, demo scale | Documented, not yet built |
| **Phase 1** | Multi-role allocation, fairness auditing, logging | Planned |
| **Phase 2** | Millions of records, sharding, distributed indexing | Planned |
| **Phase 3** | Continuous enhancements, A/B testing, optimization | Post-launch |

Detailed phase breakdown and deliverables are in [`docs/13-phasing-roadmap.md`](docs/13-phasing-roadmap.md).

---

## Getting Started

### I want to understand the system (5–15 minutes)

1. Read [`docs/01-system-overview.md`](docs/01-system-overview.md) — high-level architecture and stakeholders
2. Skim the three core sections: [`03-matching-and-scoring.md`](docs/03-matching-and-scoring.md), [`04-scheduling-and-allocation.md`](docs/04-scheduling-and-allocation.md), [`05-minimum-skill-set.md`](docs/05-minimum-skill-set.md)
3. Look at the phasing in [`13-phasing-roadmap.md`](docs/13-phasing-roadmap.md) to see what's MVP vs. future work

### I want to build it (implementer's path)

```bash
git clone https://github.com/tejaswin-amara/Resume_Job_Matching_Talent_Marketplace_Engine.git
cd Resume_Job_Matching_Talent_Marketplace_Engine
```

Then:

1. **Read the foundation:** [`docs/01-system-overview.md`](docs/01-system-overview.md) + [`docs/02-data-model-and-normalization.md`](docs/02-data-model-and-normalization.md)
2. **Check the scope:** What's Phase 0 MVP? See [`docs/13-phasing-roadmap.md`](docs/13-phasing-roadmap.md)
3. **Code from pseudocode:** For each algorithm, go to [`docs/11-schemas-workflows-pseudocode.md`](docs/11-schemas-workflows-pseudocode.md) and transcribe directly. This is your spec.
4. **Test as you go:** Each feature needs a known-answer unit test before merge. See [`docs/10-operational-considerations.md`](docs/10-operational-considerations.md) for testing strategy.

### I want the full picture (reference)

→ Read [`FULL-DOCUMENTATION.md`](FULL-DOCUMENTATION.md) (all 13 sections concatenated, single file, auto-generated)

---

## Repository Structure

```
Resume_Job_Matching_Talent_Marketplace_Engine/
│
├── 📖 README.md                        (you are here)
├── 📜 LICENSE                          (academic use)
├── 📋 FULL-DOCUMENTATION.md            (auto-generated, CI-synced)
│
├── 📁 ABSTRACT/                        (grading submission)
│   ├── README.md                       (team & submission info)
│   └── DSA-3 Project Abstract.pdf      (official abstract)
│
├── 📁 docs/                            (13 engineering sections)
│   ├── 01-system-overview.md
│   ├── 02-data-model-and-normalization.md
│   ├── 03-matching-and-scoring.md
│   ├── 04-scheduling-and-allocation.md
│   ├── 05-minimum-skill-set.md
│   ├── 06-data-pipeline-and-indexing.md
│   ├── 07-api-and-service-contracts.md
│   ├── 08-security-privacy-compliance.md
│   ├── 09-deployment-architecture.md
│   ├── 10-operational-considerations.md
│   ├── 11-schemas-workflows-pseudocode.md   (← START HERE for coding)
│   ├── 12-documentation-artifacts.md
│   └── 13-phasing-roadmap.md                (← MVP scope & timeline)
│
├── 📁 scripts/
│   └── build_full_documentation.py     (keeps FULL-DOCUMENTATION.md in sync)
│
├── 📁 backend/                         (Spring Boot microservices)
│   ├── src/                            (Ingestion, Matching, Allocation)
│   ├── pom.xml
│   └── Dockerfile
│
├── 📁 frontend/                        (Next.js + TypeScript)
│   ├── app/                            (React components)
│   ├── package.json
│   └── Dockerfile
│
├── 📁 engine/                          (Python algorithms & ML)
│   ├── algorithms/                     (matching, allocation, set cover)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml                  (local dev: all 3 services)
├── commitlint.config.js                (conventional commits)
└── .github/workflows/
    └── (CI/CD: docs sync, link validation)
```

---

## Team & Attribution

**Team 36 · Section 10**  
KL Deemed to be University, Hyderabad · DSA-3 (25CS2103E) · Odd Semester 2026–27

| Name | Roll Number |
|------|---|
| Tejaswin Amara | 2520090104 |
| Sai Ram Pragnay Murikipudi | 2520090081 |

**Course Guide:** Miss. Chandusha Kanda, Assistant Professor, CSIT

See [`ABSTRACT/README.md`](ABSTRACT/README.md) for full submission details and abstract PDF.

---

## License

This is an academic project. See [`LICENSE`](LICENSE) for terms.

---

<div align="center">

**Built by Team 36 for DSA-3 (25CS2103E) at KLBCH**

Questions? Open an issue. Contributions welcome.

</div>
