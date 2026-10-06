# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-06
### Added
- **React Bits Frontend Suite:** Replaced custom and third-party UI primitives with high-performance React Bits components (`SpotlightCard`, `ShinyText`, `AnimatedBadge`, `AnimatedProgress`, `Squares`, `FadeContent`, `CountUp`, `StarBorder`).
- **OpenTelemetry Instrumentation:** Integrated distributed tracing export and middleware in `api/telemetry/`.
- **Production Connection Pooling:** Configured SQLAlchemy async engine with `pool_pre_ping=True`, `pool_recycle=1800`, `pool_size=20`, and `max_overflow=10`.
- **Readiness Probes:** Implemented genuine PostgreSQL connectivity check on `/health/ready` with RFC 7807 503 error handling.
- **Supply-Chain Hardening:** Pinned `aquasecurity/trivy-action@0.28.0` in CI and added a comprehensive `.dockerignore`.

### Changed
- **Async Event-Loop Architecture:** Wrapped all CPU-bound operations (`EmbeddingService.encode`, `BaseParser.parse`, `SkillExtractor.extract`, `HybridMatcher.match`) in `asyncio.to_thread` across all FastAPI controllers.
- **CORS Hardening:** Replaced wildcard origin permissions with an explicit trusted origin whitelist.
- **Core Engine Bug Fixes:**
  - `dinic.py`: Added `source == sink` guard returning `0.0`.
  - `bitmask_tsp.py`: Eliminated start node duplication during tour reconstruction.
  - `marketplace_network.py`: Mapped multi-headcount job requisitions to bipartite capacity constraints.
  - `parallel_primitives.py`: Preserved identity elements for negative range parallel prefix scans.

## [1.0.0] - 2026-09-30
### Added
- Complete ground-up re-engineering of the Resume Job Matching Talent Marketplace Engine
- Zero-library DSA algorithmic core
- Hybrid matching engine (Vector + Aho-Corasick + DP)
- FastAPI backend with Pydantic V2 schemas
- Next.js 14 frontend dashboard
- Docker compose orchestration and CI/CD pipelines
