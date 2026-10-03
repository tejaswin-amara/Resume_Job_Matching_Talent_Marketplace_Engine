# Zero-Downtime Rollback Procedure

## Context
Deployments to the Talent Marketplace Engine should be fully reversible without taking the system offline, minimizing disruption to candidates and recruiters.

## Rollback Steps

### 1. Identify Failure
Monitor Prometheus metrics (e.g., HTTP 5xx rate > 1%) or Sentry error spikes post-deployment.

### 2. Frontend / API Reversion (Stateless)
If the issue is in the FastAPI backend or Next.js frontend:
1. Revert the container image tag in `docker-compose.yml` or Kubernetes deployment to the previous stable SHA.
2. Trigger a rolling restart:
   ```bash
   docker-compose up -d --no-deps backend frontend
   ```
3. Verify health checks pass.

### 3. Database Schema Rollback (Stateful)
If the issue stems from a bad Alembic migration:
1. DO NOT revert the API code first if it relies on the new schema.
2. Downgrade the database using Alembic:
   ```bash
   alembic downgrade -1
   ```
   *Note: Ensure all migrations have properly defined `downgrade()` functions.*
3. Once the schema is reverted, rollback the API and Frontend container images as detailed in Step 2.

### 4. Vector Embedding Incompatibilities
If a new sentence-transformer model was deployed and performs poorly:
1. Roll back the embedding service container.
2. The database may contain a mix of old and new vectors. Trigger a background job to recompute vectors using the older stable model.
