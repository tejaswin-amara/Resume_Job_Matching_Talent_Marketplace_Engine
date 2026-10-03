# Incident Response Runbook

This document defines triage and response procedures for incidents in the Talent Marketplace Engine.

## Incident Severity Levels
- **SEV-1 (Critical):** Core matching engine down, database inaccessible, or massive data breach. All hands on deck.
- **SEV-2 (High):** Embedding service degraded, significant latency in resume processing, or major UI bugs affecting core workflows.
- **SEV-3 (Medium):** Minor UI glitches, non-critical API endpoints failing.

## Triage Procedure
1. **Acknowledge:** On-call engineer acknowledges the PagerDuty alert within 5 minutes.
2. **Investigate:**
   - Check FastAPI backend logs (`docker logs backend`).
   - Check Postgres CPU/Memory and pgvector index health.
   - Verify Embedding Service queue.
3. **Mitigate:**
   - Apply circuit breakers or rate limits if under DDoS.
   - Restart affected containers.
   - Scale up replica counts if bottleneck is CPU (especially Embedding Service).
4. **Communicate:** Notify stakeholders via Slack `#incidents` channel. Update status page.
5. **Post-Mortem:** Conduct a blameless post-mortem within 48 hours for any SEV-1/SEV-2.
