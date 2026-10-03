## 2026-09-29T08:28:18Z

You are teamwork_preview_explorer_survey_backend_2.
Your working directory is: c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_backend_2

MANDATORY: You MUST read ORIGINAL_REQUEST.md at:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md

Your mission:
Investigate and design the technical architecture for the Backend & ML Data Layer:
1. Examine the environment, Python runtime, PostgreSQL + pgvector setup, and package dependencies.
2. Design database models and schema:
   - Candidates, Resumes (vector embedding, parsed entities, file metadata)
   - Job Postings (vector embedding, required/preferred skills, exp/edu requirements)
   - Skills (taxonomy, normalized names, synonyms)
   - Match Results (per-signal scores, explainability breakdowns)
   - Alembic migration strategy and realistic seed dataset (>=10 jobs, >=15 candidates)
3. Design ML/NLP engine architecture:
   - Sentence-transformers embedding generation (model choice, e.g., all-MiniLM-L6-v2 or lightweight alternative, offline/caching fallback)
   - Resume parser supporting PDF, DOCX, and plain text with entity extraction (skills, years of experience, education, contact info)
   - ATS Explainability engine generating suggestions and gap analysis
4. Unit and integration test architecture with pytest, test coverage strategy, and ruff linting setup.

Write your complete findings and architecture recommendations to:
c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_backend_2\handoff.md

Update progress.md in your working directory.
When done, send a concise message back to the orchestrator referencing the handoff path.
