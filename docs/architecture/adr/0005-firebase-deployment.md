# 5. Firebase Deployment Strategy

Date: 2026-10-10

## Status

Accepted

## Context

The system needs to be deployed to a Google/Firebase-hosted production system without third-party services (Neon, Supabase, Render, etc.). The existing architecture uses Python (FastAPI), SQLAlchemy, Alembic, and PostgreSQL + pgvector for the backend, and Next.js 14 for the frontend. There are two primary paths:
1. Strict rewrite using native Firebase services (Firestore, Firebase Functions).
2. Preserving the stack using Firebase App Hosting + Google Cloud Run + Cloud SQL.

## Decision

We will follow the recommended path of **preserving the existing product and algorithms** by utilizing Firebase and Google Cloud components that support our current architecture:

- **Frontend:** Firebase App Hosting (supports Next.js).
- **API and ML Runtime:** Google Cloud Run (containerized FastAPI).
- **Database:** Google Cloud SQL (PostgreSQL with pgvector extension).
- **Storage:** Cloud Storage for Firebase.
- **Identity:** Firebase Authentication.
- **Routing:** Firebase Hosting rewrites / App Hosting.
- **Secrets:** Google Cloud Secret Manager.

## Consequences

- We avoid a complete rewrite of the ML features, preserving the usage of `pgvector` and `SentenceTransformers`.
- Deployment requires orchestration of Firebase resources and Google Cloud resources (Cloud Run and Cloud SQL) via Terraform, gcloud CLI, or Firebase CLI where supported.
- Costs will involve Cloud Run and Cloud SQL usage under the chosen billing plan.
- The project completely drops Vercel and any other external PaaS dependencies.
