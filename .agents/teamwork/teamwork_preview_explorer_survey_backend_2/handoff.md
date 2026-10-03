# Handoff Report: Backend & ML Data Layer Technical Architecture

**Agent**: `teamwork_preview_explorer_survey_backend_2`  
**Working Directory**: `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_backend_2`  
**Milestone**: Phase 0 — Survey & Technical Architecture Specification  
**Recipient**: Orchestrator (`teamwork_preview_orchestrator_1`)  

---

## 1. Observation

### 1.1 Environment & System Telemetry
- **Host OS**: Windows (x86_64), PowerShell shell.
- **Python Runtime**: Python 3.13.14 (`C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0`).
- **Package Manager**: `uv 0.11.28` installed and fully operational.
- **Container Infrastructure**: `Docker 29.6.1` daemon is running.
  - Image `pgvector/pgvector:pg16` is **pre-pulled and cached locally** (`sha256:1d533553fe...`, size 156 MB).
  - Port `5432` is currently unallocated and free for PostgreSQL binding.
- **Node & Frontend Environment**: Node `v26.7.0`, npm `11.19.0`, pnpm `11.24.0` available.
- **Linting & Code Quality**: `ruff 0.16.9` operational via `uvx ruff`.
- **Existing System Packages**: `fastapi 0.141.1`, `uvicorn 0.52.1`, `pydantic 2.13.4`, `pytest 9.1.1`, `httpx 0.28.1`, `pdfminer.six 20260107`, `python-multipart 0.0.32`.
- **Dependency Resolution Test**: A dry-run resolution with `uv` against Python 3.13 succeeded in **1.67s** resolving:
  - `torch==2.14.0`, `sentence-transformers==6.1.0`, `pgvector==0.5.0`, `sqlalchemy==2.1.1`, `asyncpg==0.31.0`, `psycopg[binary]==3.3.6`, `alembic==1.20.0`, `pydantic-settings==2.15.0`, `python-docx==1.2.0`, `pypdf==6.19.0`.
- **External Network Connectivity**: HTTPS connectivity to `https://huggingface.co` verified (`HTTP 200 OK`).

---

## 2. Logic Chain

### 2.1 Architecture Principles & Directory Layout
To satisfy the requirements in `ORIGINAL_REQUEST.md` (R1, R2, R4), the backend must follow a clean **Domain-Driven, Layered Architecture**:
```
backend/
├── alembic/
│   ├── env.py                      # Async SQLAlchemy + pgvector migration runner
│   ├── script.py.mako              # Migration template
│   └── versions/                   # Migration scripts (0001_initial_schema.py)
├── alembic.ini                     # Alembic configuration
├── pyproject.toml                  # Project metadata, dependencies, ruff & pytest config
├── Dockerfile                      # Production multi-stage backend container
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entrypoint & lifespan
│   ├── config.py                   # Pydantic Settings (DB URLs, model params, weights)
│   ├── core/
│   │   ├── database.py             # Async engine, sessionmaker, Base model
│   │   ├── exceptions.py           # RFC 7807 problem details handler
│   │   └── security.py             # Input sanitization, file validator
│   ├── models/
│   │   ├── __init__.py
│   │   ├── candidate.py            # Candidate SQLAlchemy model
│   │   ├── resume.py               # Resume SQLAlchemy model (pgvector Vector(384))
│   │   ├── job.py                  # JobPosting SQLAlchemy model (pgvector Vector(384))
│   │   ├── skill.py                # Skill taxonomy model
│   │   └── match.py                # MatchResult model (per-signal scores & explainability)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── candidate.py            # Pydantic input/output schemas
│   │   ├── resume.py               # Upload response, parsed entity schemas
│   │   ├── job.py                  # Job create, query, response schemas
│   │   └── match.py                # Match breakdown & explainability schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding.py            # SentenceTransformers + deterministic fallback
│   │   ├── parser.py               # Multi-format parser (PDF, DOCX, TXT)
│   │   ├── extractor.py            # Entity extraction (skills, exp, edu, contact)
│   │   ├── matcher.py              # 4-signal hybrid scoring engine
│   │   └── explainability.py       # ATS diagnostic & improvement suggestions
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py           # API v1 aggregator
│   │   │   ├── resumes.py          # /api/v1/resumes/upload
│   │   │   ├── jobs.py             # /api/v1/jobs CRUD & /api/v1/jobs/{id}/matches
│   │   │   └── match.py            # /api/v1/match/adhoc
│   │   └── health.py               # /health/live, /health/ready
│   └── seed/
│       ├── __init__.py
│       ├── seed_data.py            # Comprehensive dataset (12 jobs, 16 candidates)
│       └── runner.py               # Standalone execution CLI for seeding
└── tests/
    ├── conftest.py                 # Shared fixtures (in-memory SQLite/Postgres, mock models)
    ├── unit/
    │   ├── test_scoring.py         # Exact formula, edge cases, zero-division, bounds
    │   ├── test_parser.py          # PDF, DOCX, TXT parsers & sanitizers
    │   ├── test_extractor.py       # Skills taxonomy, experience years, education rank
    │   └── test_explainability.py  # Gap analysis & recommendation engine
    └── integration/
        ├── test_api_resumes.py     # Resume upload endpoint & validations
        ├── test_api_jobs.py        # Jobs CRUD & pagination
        ├── test_api_matches.py     # Job candidate matching & adhoc endpoint
        └── test_health.py          # /health/live and /health/ready
```

---

### 2.2 Database Models & Schema Specification

#### 2.2.1 Vector Column & Cross-Engine Compatibility
- Model: `all-MiniLM-L6-v2` produces `384`-dimensional normalized vectors.
- Pgvector representation: `Vector(384)` from `pgvector.sqlalchemy`.
- Test Compatibility Decorator: For running unit tests without external Postgres, the schema can define a custom `VectorType` that compiles to `Vector(384)` on PostgreSQL and `JSON` on SQLite:
  ```python
  from sqlalchemy.types import TypeDecorator
  from pgvector.sqlalchemy import Vector
  from sqlalchemy import JSON


  class CompatibleVector(TypeDecorator):
      impl = Vector(384)
      cache_ok = True

      def load_dialect_impl(self, dialect):
          if dialect.name == "postgresql":
              return dialect.type_descriptor(Vector(384))
          return dialect.type_descriptor(JSON())
  ```

#### 2.2.2 Entity Relationship Diagram (Schema Details)

1. **`candidates` Table**:
   - `id`: `UUID` (PK, default `uuid4`)
   - `first_name`: `String(100)`, NOT NULL
   - `last_name`: `String(100)`, NOT NULL
   - `email`: `String(255)`, UNIQUE, INDEX, NOT NULL
   - `phone`: `String(50)`, NULLABLE
   - `linkedin_url`: `String(255)`, NULLABLE
   - `github_url`: `String(255)`, NULLABLE
   - `location`: `String(150)`, NULLABLE
   - `created_at`: `DateTime(timezone=True)`, server_default=now()
   - `updated_at`: `DateTime(timezone=True)`, onupdate=now()
   - *Relationships*: `resumes` (1-to-many, cascade="all, delete-orphan"), `match_results` (1-to-many).

2. **`resumes` Table**:
   - `id`: `UUID` (PK, default `uuid4`)
   - `candidate_id`: `UUID`, FK(`candidates.id`, ondelete="CASCADE"), INDEX, NOT NULL
   - `file_name`: `String(255)`, NOT NULL
   - `file_type`: `String(100)`, NOT NULL (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`)
   - `file_size_bytes`: `Integer`, NOT NULL
   - `raw_text`: `Text`, NOT NULL
   - `parsed_data`: `JSONB` / `JSON`, NOT NULL (stores extracted contact info, skills array, experience years, education items, certifications)
   - `embedding`: `CompatibleVector(384)`, NOT NULL
   - `is_active`: `Boolean`, default=True, INDEX
   - `created_at`: `DateTime(timezone=True)`, server_default=now()
   - `updated_at`: `DateTime(timezone=True)`, onupdate=now()
   - *Indices*:
     - HNSW Index: `CREATE INDEX ix_resumes_embedding_hnsw ON resumes USING hnsw (embedding vector_cosine_ops);`
     - B-Tree Index: `(candidate_id, is_active)`

3. **`job_postings` Table**:
   - `id`: `UUID` (PK, default `uuid4`)
   - `title`: `String(200)`, INDEX, NOT NULL
   - `company`: `String(150)`, INDEX, NOT NULL
   - `department`: `String(100)`, NULLABLE
   - `location`: `String(150)`, NOT NULL
   - `employment_type`: `String(50)`, default="Full-time"
   - `description`: `Text`, NOT NULL
   - `required_skills`: `JSONB` / `JSON`, NOT NULL (list of normalized string skills)
   - `preferred_skills`: `JSONB` / `JSON`, NOT NULL (list of normalized string skills)
   - `min_years_experience`: `Float`, default=0.0, NOT NULL
   - `max_years_experience`: `Float`, NULLABLE
   - `required_education_level`: `String(50)`, default="bachelor", NOT NULL (`none`, `high_school`, `associate`, `bachelor`, `master`, `doctorate`)
   - `salary_min`: `Numeric(12, 2)`, NULLABLE
   - `salary_max`: `Numeric(12, 2)`, NULLABLE
   - `currency`: `String(10)`, default="USD"
   - `is_active`: `Boolean`, default=True, INDEX
   - `embedding`: `CompatibleVector(384)`, NOT NULL
   - `created_at`: `DateTime(timezone=True)`, server_default=now()
   - `updated_at`: `DateTime(timezone=True)`, onupdate=now()
   - *Indices*:
     - HNSW Index: `CREATE INDEX ix_jobs_embedding_hnsw ON job_postings USING hnsw (embedding vector_cosine_ops);`
     - B-Tree Index: `(is_active, created_at DESC)`

4. **`skills` Table (Taxonomy & Aliases)**:
   - `id`: `UUID` (PK, default `uuid4`)
   - `name`: `String(100)`, UNIQUE, INDEX, NOT NULL (normalized lower, e.g., "fastapi", "postgresql", "kubernetes")
   - `display_name`: `String(100)`, NOT NULL (e.g., "FastAPI", "PostgreSQL", "Kubernetes")
   - `category`: `String(50)`, INDEX, NOT NULL ("Backend", "Frontend", "Database", "DevOps/Cloud", "ML/Data", "Architecture", "Mobile", "Security")
   - `synonyms`: `JSONB` / `JSON`, default=[] (e.g., `["postgres", "pgsql", "psql"]`, `["k8s"]`, `["py", "python3"]`)
   - `created_at`: `DateTime(timezone=True)`, server_default=now()

5. **`match_results` Table (Persistent Matches & Leaderboard)**:
   - `id`: `UUID` (PK, default `uuid4`)
   - `job_id`: `UUID`, FK(`job_postings.id`, ondelete="CASCADE"), INDEX, NOT NULL
   - `resume_id`: `UUID`, FK(`resumes.id`, ondelete="CASCADE"), INDEX, NOT NULL
   - `candidate_id`: `UUID`, FK(`candidates.id`, ondelete="CASCADE"), INDEX, NOT NULL
   - `total_score`: `Float`, INDEX, NOT NULL (0.00 to 100.00)
   - `semantic_score`: `Float`, NOT NULL (0.0 to 1.0)
   - `skills_score`: `Float`, NOT NULL (0.0 to 1.0)
   - `experience_score`: `Float`, NOT NULL (0.0 to 1.0)
   - `education_score`: `Float`, NOT NULL (0.0 to 1.0)
   - `score_breakdown`: `JSONB` / `JSON`, NOT NULL (raw scores, weighted values, percentage shares)
   - `matched_skills`: `JSONB` / `JSON`, NOT NULL (list of matched skills)
   - `missing_skills`: `JSONB` / `JSON`, NOT NULL (list of required/preferred skills missing)
   - `experience_analysis`: `JSONB` / `JSON`, NOT NULL (candidate yrs, job req yrs, delta, status)
   - `education_analysis`: `JSONB` / `JSON`, NOT NULL (candidate degree, job required degree, status)
   - `improvement_suggestions`: `JSONB` / `JSON`, NOT NULL (ordered list of actionable ATS recommendations)
   - `created_at`: `DateTime(timezone=True)`, server_default=now()
   - *Constraints & Indices*:
     - Unique constraint: `UNIQUE(job_id, resume_id)`
     - Leaderboard composite index: `(job_id, total_score DESC)`
     - Candidate portal index: `(candidate_id, total_score DESC)`

---

### 2.3 Alembic Migration Strategy

1. **Async Migration Configuration (`alembic/env.py`)**:
   - Must import `from pgvector.sqlalchemy import Vector` and base models `from app.core.database import Base`.
   - Setup `run_migrations_online` using `async_engine_from_config` with `asyncpg` or synchronous connection wrapper.
2. **Initial Migration (`0001_initial_schema.py`)**:
   - `upgrade()`:
     ```python
     # 1. Enable pgvector extension
     op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
     # 2. Create tables: candidates, resumes, job_postings, skills, match_results
     # 3. Create HNSW indexes on vector columns:
     op.execute("""
         CREATE INDEX IF NOT EXISTS ix_resumes_embedding_hnsw
         ON resumes USING hnsw (embedding vector_cosine_ops)
         WITH (m = 16, ef_construction = 64);
     """)
     op.execute("""
         CREATE INDEX IF NOT EXISTS ix_job_postings_embedding_hnsw
         ON job_postings USING hnsw (embedding vector_cosine_ops)
         WITH (m = 16, ef_construction = 64);
     """)
     ```
   - `downgrade()`:
     - Drop tables and indices cleanly with cascade.

---

### 2.4 Realistic Seed Dataset Specification (>=10 Jobs, >=15 Candidates)

The seed script will populate **12 diverse job postings** and **16 candidate profiles** across multiple disciplines and seniority tiers to thoroughly exercise the ATS scoring engine:

#### Job Postings (12 Roles)
1. **Senior Backend Engineer** (Python / FastAPI / PostgreSQL / Docker, min 5 yrs, Bachelor)
2. **Staff ML / NLP Engineer** (PyTorch / Transformers / HuggingFace / MLOps, min 6 yrs, Master)
3. **Full-Stack Software Engineer** (Next.js / TypeScript / React / Node.js / PostgreSQL, min 3 yrs, Bachelor)
4. **Lead DevOps & Cloud Architect** (Kubernetes / Terraform / AWS / CI/CD, min 7 yrs, Bachelor)
5. **Senior Data Engineer** (Apache Spark / Kafka / Airflow / SQL, min 5 yrs, Bachelor)
6. **Principal Security Engineer** (AppSec / Cloud Security / OAuth / Penetration Testing, min 8 yrs, Bachelor)
7. **Frontend Engineer** (React / Tailwind CSS / Web Performance / Next.js, min 2 yrs, Associate)
8. **Mobile Engineer (iOS/Android)** (React Native / Swift / Kotlin / GraphQL, min 4 yrs, Bachelor)
9. **Site Reliability Engineer (SRE)** (Prometheus / Grafana / Linux / Incident Management, min 4 yrs, Bachelor)
10. **Technical Product Manager** (Agile / Roadmap / SQL / User Stories, min 4 yrs, Bachelor)
11. **QA / Automation Engineer (SDET)** (Pytest / Playwright / CI/CD / Docker, min 3 yrs, Bachelor)
12. **Junior Software Engineer** (Python / REST APIs / Git / SQL, min 0 yrs, Bachelor)

#### Candidates (16 Profiles with Ground-Truth Profiles)
1. **Alex Chen** (Senior Backend, 6.5 yrs, Master in CS) — *Perfect fit for Job 1, high match.*
2. **Dr. Sophia Vance** (NLP Research Scientist, 7 yrs, Ph.D. in Computer Science) — *Top match for Job 2.*
3. **Marcus Brody** (Full-Stack Dev, 4 yrs, Bachelor) — *Strong fit for Job 3.*
4. **Elena Rostova** (Cloud Infrastructure Lead, 9 yrs, Bachelor) — *Dominant fit for Job 4.*
5. **David Kim** (Data Engineer, 5.5 yrs, Master) — *Strong fit for Job 5.*
6. **Zara Patel** (Security Architect, 8 yrs, Bachelor) — *Top fit for Job 6.*
7. **Lucas Silva** (Frontend Specialist, 3 yrs, Associate Degree) — *Strong fit for Job 7.*
8. **Chloe Bennett** (Mobile App Dev, 5 yrs, Bachelor) — *Strong fit for Job 8.*
9. **Tariq Al-Mansoor** (Systems & Reliability Engineer, 4.5 yrs, Bachelor) — *Strong fit for Job 9.*
10. **Rachel Green** (Tech PM, 5 yrs, MBA + B.S.) — *Strong fit for Job 10.*
11. **Vikram Malhotra** (SDET Engineer, 3.5 yrs, Bachelor) — *Strong fit for Job 11.*
12. **Samira Khan** (Junior Python Developer, 1 yr, Bachelor) — *Strong fit for Job 12; partial fit for Job 1.*
13. **Jordan Taylor** (Backend Mid-level, 2.5 yrs, Bachelor) — *Tests experience gap when matched with Job 1 (under min 5 yrs).*
14. **Maya Lin** (Pure Frontend React Dev, 5 yrs, Bachelor) — *Tests skill gap when applied to Job 1 (Backend) or Job 2 (ML).*
15. **Oliver Queen** (Overqualified Senior Director, 14 yrs, Master) — *Tests overqualification scoring calibration.*
16. **Nia Jackson** (Bootcamp Graduate / Career Switcher, 0.5 yrs, High School) — *Tests boundary/underqualification behavior.*

Each candidate will have parsed entity JSON, raw resume text, and pre-generated 384-dimensional vector embeddings seeded so full search, ranking, and explainability work immediately out-of-the-box.

---

### 2.5 ML/NLP Engine Architecture

#### 2.5.1 Embedding Service & Lightweight Fallback
- **Model Choice**: `sentence-transformers/all-MiniLM-L6-v2`
  - Dimensions: 384
  - Parameter count: 22.7M (~80 MB download)
  - Inference speed: ~15ms on CPU per document
  - Context window: 512 tokens with automatic sliding window chunking & mean pooling
- **Embedding Generation Contract**:
  ```python
  class EmbeddingService(Protocol):
      def embed_text(self, text: str) -> list[float]: ...
      def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
  ```
- **Deterministic Lightweight Fallback (Zero-Dependency)**:
  For environments without PyTorch/HuggingFace access, network air-gapping, or high-speed unit testing, a deterministic term-frequency hashing vectorizer:
  - Tokenizes input, extracts unigrams and bigrams.
  - Hashes tokens modulo 384 with Murmur/SHA256 salt.
  - Normalizes L2 norm: $\hat{v} = \frac{v}{\|v\|_2}$ ensuring unit length.
  - Semantic properties: Identical texts yield cosine similarity = 1.0; texts sharing common vocabulary yield proportional positive cosine similarity; orthogonal texts yield ~0.0.
  - Switching mechanism: Driven by `EMBEDDING_PROVIDER` env var (`"sentence-transformers"` default with automatic graceful fallback to `"lightweight"` if torch/transformers fail).

#### 2.5.2 Multi-Format Resume Parser & Sanitizer
- **Supported Formats**: `.pdf`, `.docx`, `.txt`
- **Validation & Sanitization**:
  1. File size check: enforce max 10 MB.
  2. Magic byte / MIME type validation:
     - PDF: Check `%PDF-` signature.
     - DOCX: Check zip header `PK\x03\x04` and confirm `word/document.xml` presence.
     - Plain text: UTF-8 / ASCII / Latin-1 decode validation.
  3. Text sanitization:
     - Strip null bytes (`\x00`), Unicode control characters, carriage return artifacts (`\r\n` -> `\n`).
     - Collapse repetitive whitespace, trim leading/trailing noise.
- **Parsing Engines**:
  - **PDF**: Primary via `pdfminer.high_level.extract_text` or `pypdf.PdfReader` with multi-page concatenation.
  - **DOCX**: Primary via `python-docx` iterating `doc.paragraphs` and `doc.tables`. Secondary zero-dependency fallback via `zipfile` extracting XML text nodes from `word/document.xml`.
  - **Plain Text**: Direct decoded text.

#### 2.5.3 Entity Extraction Engine
1. **Contact Information**:
   - `email`: Regex `r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'`
   - `phone`: Regex `r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'`
   - `linkedin`: Regex `r'linkedin\.com/in/([a-zA-Z0-9_-]+)'`
   - `github`: Regex `r'github\.com/([a-zA-Z0-9_-]+)'`
   - `name`: Top header heuristics discarding common headings ("Resume", "CV", contact tokens).
2. **Skills Extraction**:
   - Comprehensive Skill Taxonomy dictionary (>200 tech skills mapped to canonical keys).
   - Word boundary regex with punctuation support (e.g. `\bC\+\+\b`, `\bC#\b`, `\b\.NET\b`, `\bNode\.js\b`).
   - Synonym mapping:
     - `"postgres"`, `"pgsql"`, `"postgresql"` -> `"postgresql"`
     - `"k8s"`, `"kubernetes"` -> `"kubernetes"`
     - `"py"`, `"python3"`, `"python"` -> `"python"`
     - `"react"`, `"reactjs"`, `"react.js"` -> `"react"`
     - `"docker-compose"`, `"docker compose"` -> `"docker"`
3. **Years of Experience**:
   - Primary: Sum of date spans extracted from employment history (e.g., `Jan 2020 - Mar 2023` = 3.2 yrs; `2018 - Present` = current delta).
   - Secondary: Explicit career statement regex: `r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)'`.
   - Default: If no years detect, return `0.0` and mark in ATS diagnostic.
4. **Education Level**:
   - Rank hierarchy:
     - `doctorate` (Rank 5): PhD, Ph.D., Doctorate, Doctor of Philosophy
     - `master` (Rank 4): Master, M.S., MS, M.A., MBA, M.Tech, M.Eng
     - `bachelor` (Rank 3): Bachelor, B.S., BS, B.A., B.Tech, B.E., Undergraduate
     - `associate` (Rank 2): Associate, A.S., A.A., Diploma
     - `high_school` (Rank 1): High School, Secondary School, GED
     - `none` (Rank 0): Not detected
   - Scans resume text for highest achieved degree level and extracts field of study and institution.

---

### 2.6 Hybrid Scoring & ATS Explainability Engine

#### 2.6.1 Exact Mathematical Formula
Per `ORIGINAL_REQUEST.md`:
$$\text{Total Score} = 100 \times \left( 0.40 \times S_{\text{semantic}} + 0.35 \times S_{\text{skill}} + 0.15 \times S_{\text{experience}} + 0.10 \times S_{\text{education}} \right)$$

Where:
1. **$S_{\text{semantic}}$ (Weight: 0.40)**:
   - Cosine similarity between resume embedding $v_R$ and job embedding $v_J$:
     $$S_{\text{semantic}} = \max\left(0.0, \min\left(1.0, \frac{v_R \cdot v_J}{\|v_R\| \|v_J\|}\right)\right)$$
   - Boundary checks:
     - Zero vector or empty text $\implies 0.0$.
     - Identical text $\implies 1.0$.

2. **$S_{\text{skill}}$ (Weight: 0.35)**:
   - Let $R$ = set of required skills, $P$ = set of preferred skills, $C$ = candidate skills.
   - If $|R| > 0$ and $|P| > 0$:
     $$S_{\text{skill}} = 0.75 \times \frac{|C \cap R|}{|R|} + 0.25 \times \frac{|C \cap P|}{|P|}$$
   - If $|R| > 0$ and $|P| == 0$:
     $$S_{\text{skill}} = \frac{|C \cap R|}{|R|}$$
   - If $|R| == 0$ and $|P| > 0$:
     $$S_{\text{skill}} = \frac{|C \cap P|}{|P|}$$
   - Edge case (Empty skill sets $|R \cup P| == 0$):
     - Job specifies no skills: Candidate automatically satisfies requirements: $S_{\text{skill}} = 1.0$.

3. **$S_{\text{experience}}$ (Weight: 0.15)**:
   - Candidate years $Y_C$, Job required years $Y_{\text{req}}$.
   - Edge case ($Y_{\text{req}} \le 0$):
     - Requirement is 0 (entry-level): $S_{\text{experience}} = 1.0$.
   - Normal case ($Y_{\text{req}} > 0$):
     - If $Y_C \ge Y_{\text{req}} \implies S_{\text{experience}} = 1.0$.
     - If $Y_C < Y_{\text{req}} \implies S_{\text{experience}} = \max\left(0.0, \frac{Y_C}{Y_{\text{req}}}\right)$.

4. **$S_{\text{education}}$ (Weight: 0.10)**:
   - Candidate rank $L_C \in [0, 5]$, Job required rank $L_{\text{req}} \in [0, 5]$.
   - If $L_{\text{req}} == 0$ or $L_{\text{req}} == \text{"none"} \implies S_{\text{education}} = 1.0$.
   - If $L_C \ge L_{\text{req}} \implies S_{\text{education}} = 1.0$.
   - If $L_C < L_{\text{req}}$:
     $$S_{\text{education}} = \max\left(0.0, 1.0 - 0.25 \times (L_{\text{req}} - L_C)\right)$$
     *(e.g., Bachelor [3] applying for Master [4] gets $1.0 - 0.25 = 0.75$; High School [1] gets $1.0 - 0.75 = 0.25$)*.

#### 2.6.2 ATS Diagnostic & Improvement Generator
The explainability engine synthesizes:
- **`matched_skills`**: List of canonical names present in both candidate and job.
- **`missing_skills`**: List of required and preferred skills not found in candidate resume.
- **`score_breakdown`**:
  - Per-signal raw score ($0.0 - 1.0$)
  - Weight ($0.40, 0.35, 0.15, 0.10$)
  - Points earned ($0.0 - 40.0, 0.0 - 35.0, 0.0 - 15.0, 0.0 - 10.0$)
  - Diagnostic human explanation
- **`improvement_suggestions`**:
  - Skill gaps: *"Missing critical required skill: Add verified experience with **Kubernetes** to your resume."*
  - Experience gaps: *"Experience gap: Job requires 5.0 years but resume reflects 3.0 years. Highlight relevant internships, open-source contributions, or freelance projects."*
  - Education alignment: *"Education gap: Position prefers Master degree; ensure to emphasize advanced certifications or specialized coursework."*
  - Formatting / ATS readability tips: *"Add quantifiable impact metrics (e.g., 'reduced latency by 30%') to strengthen semantic relevance."*

---

### 2.7 REST API Endpoints Specification

1. **`POST /api/v1/resumes/upload`**
   - Content-Type: `multipart/form-data`
   - Form parameters: `file: UploadFile`, `candidate_id: Optional[UUID]`, `first_name: Optional[str]`, `last_name: Optional[str]`, `email: Optional[EmailStr]`
   - Behavior:
     - Validates extension (`.pdf`, `.docx`, `.txt`) and mime-type.
     - Extracts raw text and cleanses input.
     - Runs entity extraction (skills, exp, edu, contact).
     - Generates 384-dimensional vector embedding.
     - Persists candidate and resume records to PostgreSQL.
     - Returns: `201 Created` with `ResumeResponse` schema.

2. **`POST /api/v1/jobs`**
   - Content-Type: `application/json`
   - Body: `JobCreateSchema` (title, company, description, required_skills, preferred_skills, min_years_experience, required_education_level, etc.)
   - Behavior:
     - Generates embedding from combined representation (`title + " " + description + " Skills: " + ", ".join(required_skills)`).
     - Persists to `job_postings`.
     - Returns: `201 Created` with `JobResponse` schema.

3. **`GET /api/v1/jobs`**
   - Query parameters: `page: int = 1`, `page_size: int = 20`, `search: Optional[str] = None`, `location: Optional[str] = None`
   - Behavior: Paginated job listings with total count.

4. **`GET /api/v1/jobs/{id}/matches`**
   - Query parameters: `top_k: int = 20`, `min_score: float = 0.0`
   - Behavior:
     - Fetches job posting embedding and requirements.
     - Queries candidate resumes using pgvector cosine distance (`1 - (resumes.embedding <=> job.embedding)`).
     - Computes hybrid scores across all active candidate resumes.
     - Ranks descending by `total_score`.
     - Persists / upserts match results in `match_results`.
     - Returns: `200 OK` with ranked candidate leaderboard and full explainability.

5. **`POST /api/v1/match/adhoc`**
   - Content-Type: `application/json`
   - Body: `AdHocMatchRequest` (`resume_text: str`, `job_description: str`, `required_skills: list[str] = []`, `min_years_experience: float = 0.0`, `required_education_level: str = "bachelor"`)
   - Behavior: Pure in-memory calculation without persisting to DB. Perfect for instant recruiter previews or testing.
   - Returns: `200 OK` with full `MatchResultResponse`.

6. **Health Endpoints**:
   - `GET /health/live`: Returns `{"status": "alive"}` (HTTP 200).
   - `GET /health/ready`: Checks PostgreSQL database connection (`SELECT 1`), pgvector extension availability, and embedding model readiness. Returns `{"status": "ready", "database": "connected", "vector_extension": "active", "embedding_model": "loaded"}` (HTTP 200) or HTTP 503 if degraded.

7. **Error Responses (RFC 7807 Problem Details)**:
   ```json
   {
     "type": "https://errors.talentmarketplace.com/validation-error",
     "title": "Invalid File Format",
     "status": 400,
     "detail": "File 'resume.exe' is not supported. Supported formats: .pdf, .docx, .txt.",
     "instance": "/api/v1/resumes/upload"
   }
   ```

---

### 2.8 Test Architecture & Linting Strategy

#### 2.8.1 Pytest Architecture
- **Fixtures (`tests/conftest.py`)**:
  - `async_client`: `httpx.AsyncClient` bound to FastAPI test app.
  - `test_db`: Isolated in-memory SQLite / test database session.
  - `mock_embedding_service`: Instant deterministic embedding fixture for zero-latency test suites.
  - `sample_job_payload`: Standardized senior engineer job posting.
  - `sample_resume_pdf`: In-memory generated PDF byte buffer with valid PDF headers.
  - `sample_resume_docx`: In-memory generated DOCX zip buffer.
- **Coverage Strategy**:
  - Command: `pytest --cov=app --cov-report=term-missing --cov-report=html`
  - Targets:
    - `app/services/matcher.py`: **100%** line and branch coverage (all 4 signals, boundary conditions, zero divisions).
    - `app/services/parser.py`: **>=90%** coverage (all 3 file types, corrupt files, empty strings).
    - `app/services/extractor.py`: **>=90%** coverage (skills taxonomy, regex patterns).
    - `app/api/`: **>=85%** coverage across all routes and error scenarios.

#### 2.8.2 Ruff Linting Configuration (`pyproject.toml`)
```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "SIM", # flake8-simplify
]
ignore = [
    "B008", # do not perform function calls in argument defaults (FastAPI Depends idiom)
]
```

---

## 3. Caveats

1. **Vector Dimension Coupling**:
   - `Vector(384)` is coupled to `all-MiniLM-L6-v2`. If the model is upgraded to a 768-dim model (e.g. `bge-base-en-v1.5`), an Alembic migration altering the column type and re-embedding existing documents would be required. The architecture isolates the dimension in `config.py` (`EMBEDDING_DIM = 384`).
2. **SQLite vs PostgreSQL in Unit Tests**:
   - SQLite does not natively support pgvector vector math. The `CompatibleVector` TypeDecorator cleanly addresses this by storing vectors as JSON in SQLite during fast unit tests, while production and integration tests leverage the cached `pgvector/pgvector:pg16` Docker container.
3. **Complex PDF Text Extraction**:
   - PDFs with non-standard font encodings or purely scanned images require OCR (Tesseract). For standard ATS operations, text-layer PDFs are standard; an explicit error is returned if a PDF contains zero extractable text ("Scanned image PDF detected — please submit a text-based PDF").

---

## 4. Conclusion

The technical architecture for the Backend & ML Data Layer is fully specified, verified against the host environment, and ready for immediate implementation.

### Key Decisions:
1. **Framework**: FastAPI (asyncpg + SQLAlchemy 2.0) with clean layered design.
2. **Vector Engine**: PostgreSQL 16 + pgvector (`all-MiniLM-L6-v2`, 384 dimensions) with HNSW cosine distance indexing (`vector_cosine_ops`).
3. **ML Fallback**: Deterministic hashing vectorizer ensures instant unit testing and zero-downtime execution even without internet access or GPU resources.
4. **Parsing**: Pure-Python multi-format extraction (`pdfminer.six` / `pypdf`, `python-docx` + stdlib XML, UTF-8 text) with zero external binary dependencies.
5. **Scoring**: Exact 4-signal calibration:
   `total = 100 * (0.40 * semantic + 0.35 * skill + 0.15 * experience + 0.10 * education)`.
6. **Data Richness**: 12 diverse job postings and 16 realistic candidate profiles with pre-computed embeddings and ground-truth match expectations.

---

## 5. Verification Method

To independently verify the environment and architectural assumptions:

```powershell
# 1. Verify Python & uv installation
python --version
uv --version

# 2. Verify pgvector Docker image availability
docker image inspect pgvector/pgvector:pg16

# 3. Verify dependency resolution
uv pip install --dry-run --system sentence-transformers pgvector sqlalchemy alembic asyncpg pydantic-settings python-docx

# 4. Verify Ruff linting
uvx ruff --version

# 5. Verification after implementation:
# Run migrations:
#   alembic upgrade head
# Run seed script:
#   python -m app.seed.runner
# Run test suite with coverage:
#   pytest --cov=app --cov-report=term-missing
# Run linter:
#   uvx ruff check .
```
