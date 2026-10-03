# System Context

This document outlines the System Context for the Resume & Job Matching Talent Marketplace Engine.

## C4 System Context Diagram

```mermaid
C4Context
    title System Context Diagram for Talent Marketplace Engine

    Person(candidate, "Candidate", "Uploads resume to find matching jobs")
    Person(recruiter, "Recruiter", "Posts job descriptions to find top talent")

    System(talentEngine, "Talent Marketplace Engine", "Matches candidates to jobs using Zero-Library DSA Core (Aho-Corasick, Dinic's Flow, Wagner-Fischer), Semantic Embeddings, and Hybrid ATS Scoring")

    System_Ext(postgres, "PostgreSQL Database", "Stores user profiles, jobs, resumes, and pgvector embeddings")
    
    Rel(candidate, talentEngine, "Uploads resume, views matches", "HTTPS")
    Rel(recruiter, talentEngine, "Posts jobs, views candidate rankings", "HTTPS")
    
    Rel(talentEngine, postgres, "Reads/Writes data and queries vectors", "TCP/IP")
```

## Description
The core system relies on a bespoke algorithmic engine that computes skill taxonomies and semantic relevance score, assigning optimal candidates via network flow algorithms.
