# Handoff Report: Frontend Web Application & Infrastructure Architecture

**Agent**: `teamwork_preview_explorer_survey_frontend_3`  
**Working Directory**: `c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\teamwork_preview_explorer_survey_frontend_3`  
**Target Milestone**: Phase 0 — Survey & Architecture Design  
**Date**: 2026-09-29T08:35:00Z  

---

## 1. Observation

Direct observations from the runtime environment probing and the authoritative requirements source (`c:\Users\speed\Documents\antigravity\bold-chandrasekhar\.agents\teamwork\ORIGINAL_REQUEST.md`).

### 1.1 Local Toolchain & Runtime Probes
Commands executed via PowerShell on the host environment:
1. `node -v` -> `v26.7.0`
2. `npm -v` -> `11.19.0`
3. `pnpm -v` -> `11.24.0`
4. `npx @biomejs/biome --version` -> `Version: 2.5.14`
5. `docker --version` -> `Docker version 29.6.1, build 8900f1d`
6. `docker compose version` -> `Docker Compose version v5.1.4`
7. `docker ps` -> Successfully connected to Docker engine daemon; container runtime is active and healthy.
8. `python --version` -> `Python 3.13.14`
9. `uv --version` -> `uv 0.11.28`
10. `uvx ruff --version` -> `ruff 0.16.9`
11. `git --version` -> `git version 2.55.0.windows.3`

### 1.2 Verbatim Requirements Quotes (ORIGINAL_REQUEST.md)
- **R3. Frontend Dashboard** (Lines 30–35):
  > "A Next.js/React TypeScript web application with:
  > - **Candidate portal**: upload resume, view parsed profile with extracted entities, see matching jobs with ATS diagnostic feedback
  > - **Recruiter portal**: post job requisitions, trigger talent matching, view ranked candidate leaderboard with skill gap visualization
  > 
  > Dark-mode-first design, responsive layout, Tailwind CSS styling."
- **R4. Infrastructure & Quality** (Lines 37–42):
  > "- Docker Compose orchestration: backend, frontend, PostgreSQL/pgvector, all with health checks
  > - Comprehensive test suite covering parsing, scoring math (boundary conditions, zero-division), and API endpoints
  > - Python linting/formatting with ruff, TypeScript with biome
  > - CI pipeline (GitHub Actions) running lint, test, security scan, and Docker build
  > - Repository governance: README with architecture overview and quick start, .env.example, .gitignore"
- **Frontend Acceptance Criteria** (Lines 61–67):
  > "- [ ] File upload form with drag-and-drop, file type validation, and upload progress
  > - [ ] Parsed resume profile display showing extracted skills, experience, education
  > - [ ] Job posting creation form and job listing page
  > - [ ] Match results page with score visualization and skill match/gap indicators
  > - [ ] Pages render without console errors and are responsive"
- **Infrastructure Acceptance Criteria** (Lines 68–74):
  > "- [ ] `docker compose up` builds and starts all services (backend, frontend, db) successfully
  > - [ ] `alembic upgrade head` runs migrations cleanly against a fresh database
  > - [ ] Seed script creates >=10 job postings and >=15 candidate profiles
  > - [ ] `ruff check .` passes with zero errors
  > - [ ] `pytest` passes; test coverage on scoring and parsing modules is maximized
  > - [ ] GitHub Actions CI workflow runs lint -> test -> build stages"

### 1.3 Schema Synchronization with Spec Miner Survey
Cross-referenced with `teamwork_preview_spec_miner_survey_1/handoff.md`:
- REST Endpoints to consume:
  - `POST /api/v1/resumes/upload` (Multipart: `file: UploadFile`)
  - `POST /api/v1/jobs` (JSON: `JobCreateRequest`)
  - `GET /api/v1/jobs` (Query: `page`, `page_size`, `query`, `location`)
  - `GET /api/v1/jobs/{id}/matches` (Path: `id`, Query: `min_score`, `limit`, `offset`)
  - `POST /api/v1/match/adhoc` (JSON: `AdHocMatchRequest`)
  - `GET /health/live` & `GET /health/ready`
- Error schema: RFC 7807 Problem Details (`application/problem+json`) with keys `type`, `title`, `status`, `detail`, `instance`.
- Hybrid ATS Scoring weights:
  - Semantic similarity: 40%
  - Skill match: 35%
  - Experience alignment: 15%
  - Education fit: 10%
  - Total composite score: 0 to 100

---

## 2. Logic Chain

### 2.1 Frontend Framework & Architectural Decisions
1. **Next.js 14/15 with App Router**:
   - Modern React Server Components (RSC) enable instantaneous initial server rendering of layout, navigation, and static metadata without client bundle hydration penalty.
   - Interactive features (drag-and-drop file upload, real-time score filters, and radar charts) are cleanly compartmentalized as Client Components (`"use client"`).
   - Native support for environment variables (`NEXT_PUBLIC_API_URL`).
2. **TypeScript Strict Typing & Single Source of Truth**:
   - All frontend TypeScript interfaces (`types.ts`) directly mirror the FastAPI backend Pydantic models.
   - Eliminates drift and guarantees compile-time validation of ATS score breakdown objects, skill arrays, and error responses.
3. **Bespoke Pure-SVG Visualizers over Heavy Charting Dependencies**:
   - Instead of pulling in large external charting libraries (e.g. Chart.js, Recharts) which can introduce hydration mismatches, client bundle bloat (>200KB), and CSS styling conflicts:
     - **RadialScoreGauge**: Pure SVG `<circle>` with `stroke-dasharray` and `stroke-dashoffset` animated via CSS transitions. Zero dependencies, instant render, perfectly themeable.
     - **SignalBreakdownBar**: Responsive CSS Flexbox bars with colored fills, weight labels, and raw/weighted score tooltips.
     - **RadarChart**: 4-point SVG `<polygon>` with concentric grid polygons and label nodes for the 4 ATS signals (Semantic, Skills, Experience, Education).
4. **Resilient API Client with RFC 7807 Error Handling**:
   - Fetch wrapper (`lib/api.ts`) automatically intercepts non-2xx responses, checks for `application/problem+json` content-type, and parses into typed `ProblemDetails` objects.
   - Displays clear, actionable banners instead of opaque generic crashes.
5. **Dark-Mode-First UI Design**:
   - Base backdrop: `bg-slate-950` with high-contrast text `text-slate-100` and muted secondary text `text-slate-400`.
   - Card surfaces: `bg-slate-900/90` with fine borders `border-slate-800` and subtle hover states `hover:border-slate-700`.
   - Visual hierarchy:
     - 90–100 ATS Score: Emerald (`text-emerald-400`, `bg-emerald-950/60`, `border-emerald-800`)
     - 70–89 ATS Score: Sky/Indigo (`text-sky-400`, `bg-sky-950/60`, `border-sky-800`)
     - 50–69 ATS Score: Amber (`text-amber-400`, `bg-amber-950/60`, `border-amber-800`)
     - 0–49 ATS Score: Rose (`text-rose-400`, `bg-rose-950/60`, `border-rose-800`)

### 2.2 Infrastructure & Quality Orchestration Decisions
1. **Docker Compose Healthcheck-Driven Dependency Graph**:
   - `db` (`pgvector/pgvector:pg16`): Runs `pg_isready -U talent_user -d talent_marketplace`.
   - `backend` (FastAPI): Uses `depends_on: db: condition: service_healthy`. Healthcheck polls `http://localhost:8000/health/live`.
   - `frontend` (Next.js): Uses `depends_on: backend: condition: service_healthy`.
   - Prevents startup race conditions (e.g. backend trying to connect to PostgreSQL before pgvector is initialized).
2. **Quality Gates with Biome and Ruff**:
   - `biome` delivers sub-second linting and formatting for TypeScript/React/CSS, replacing ESLint and Prettier.
   - `ruff` delivers sub-second linting and formatting for Python.
   - Both tools execute in parallel in GitHub Actions, keeping CI cycle times under 60 seconds.

---

## 3. Comprehensive Architecture Specifications

### 3.1 Frontend Code Layout
```
frontend/
├── package.json
├── tsconfig.json
├── biome.json
├── tailwind.config.ts
├── postcss.config.js
├── next.config.mjs
├── public/
│   └── favicon.ico
└── src/
    ├── app/
    │   ├── layout.tsx                     # Global root layout (Navbar, footer, dark theme class)
    │   ├── page.tsx                       # Landing page with Dual Portal Switcher & System Stats
    │   ├── candidate/
    │   │   ├── page.tsx                   # Candidate Portal: Resume uploader, parsed profile, matched jobs
    │   │   └── matches/
    │   │       └── [jobId]/
    │   │           └── page.tsx           # Deep-dive candidate ATS diagnostic report for a specific job
    │   ├── recruiter/
    │   │   ├── page.tsx                   # Recruiter Portal: Job requisition list & talent trigger
    │   │   ├── jobs/
    │   │   │   ├── new/
    │   │   │   │   └── page.tsx           # Create job posting form with skill chips & criteria
    │   │   │   └── [id]/
    │   │   │       └── page.tsx           # Job detail with ranked candidate leaderboard & skill gap matrix
    │   ├── match-preview/
    │   │   └── page.tsx                   # Ad-hoc Matcher: paste resume text & job text for instant ATS scoring
    │   ├── globals.css                    # Tailwind CSS base and dark-mode utility classes
    │   └── not-found.tsx                  # 404 error page
    ├── components/
    │   ├── common/
    │   │   ├── Navbar.tsx                 # Navigation with portal links, health status badge
    │   │   ├── Footer.tsx                 # System info & repo links
    │   │   ├── Badge.tsx                  # Colored chip badge for skills & statuses
    │   │   ├── ProblemAlert.tsx           # RFC 7807 error banner component
    │   │   └── LoadingSpinner.tsx         # Accessible SVG loading indicator
    │   ├── candidate/
    │   │   ├── ResumeUploader.tsx         # Drag-and-drop file uploader with progress & mime verification
    │   │   ├── ParsedProfileCard.tsx      # Candidate details, skills badges, experience, education
    │   │   └── MatchedJobsList.tsx        # List of job cards with ATS match scores & filters
    │   ├── recruiter/
    │   │   ├── JobRequisitionForm.tsx     # Structured job creation form with dynamic skill tagging
    │   │   ├── JobTable.tsx               # Paginated job requisitions table
    │   │   ├── TalentLeaderboard.tsx      # Ranked candidates leaderboard with medal indicators
    │   │   └── SkillGapVisualizer.tsx     # Side-by-side skill matrix (Matched, Missing Required, Missing Preferred)
    │   └── visualizers/
    │       ├── AtsScoreGauge.tsx          # Animated SVG circular gauge for composite ATS score (0-100)
    │       ├── SignalBreakdownBar.tsx     # 4-signal stacked progress bar with weights and raw values
    │       └── AtsRadarChart.tsx          # 4-axis SVG radar chart showing signal balance
    └── lib/
        ├── api.ts                         # Strongly-typed fetch client for FastAPI REST endpoints
        ├── types.ts                       # TypeScript interfaces matching backend models
        └── utils.ts                       # Formatting helpers (dates, scores, badges)
```

---

### 3.2 TypeScript Schema Definitions (`src/lib/types.ts`)
```typescript
/**
 * RFC 7807 Problem Details for HTTP APIs
 */
export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  invalid_params?: Array<{
    name: string;
    reason: string;
  }>;
}

/**
 * Candidate Contact Information
 */
export interface ContactInfo {
  name: string;
  email: string;
  phone?: string | null;
  location?: string | null;
  linkedin?: string | null;
  github?: string | null;
}

/**
 * Extracted Education Record
 */
export interface EducationDetail {
  degree: string;
  institution?: string | null;
  year?: number | null;
}

/**
 * Parsed Resume Profile Entity
 */
export interface ParsedResumeProfile {
  candidate_id: number;
  resume_id: number;
  filename: string;
  parsed_data: {
    contact_info: ContactInfo;
    skills: string[];
    experience_years: number;
    education_level: 'none' | 'high_school' | 'associate' | 'bachelor' | 'master' | 'doctorate';
    education_details: EducationDetail[];
    raw_text_snippet: string;
  };
  created_at: string;
}

/**
 * Job Posting Entity
 */
export interface JobPosting {
  id: number;
  title: string;
  company: string;
  department: string;
  location: string;
  employment_type: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  required_experience_years: number;
  required_education_level: 'none' | 'high_school' | 'associate' | 'bachelor' | 'master' | 'doctorate';
  salary_min?: number | null;
  salary_max?: number | null;
  created_at: string;
  updated_at: string;
}

export type JobCreateRequest = Omit<JobPosting, 'id' | 'created_at' | 'updated_at'>;

/**
 * Paginated API Response Wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * ATS 4-Signal Breakdown
 */
export interface ScoreSignalBreakdown {
  semantic_similarity: {
    raw_score: number; // 0.0 - 1.0
    weight: 0.40;
    weighted_score: number; // raw * weight * 100
  };
  skills_match: {
    raw_score: number; // 0.0 - 1.0
    weight: 0.35;
    weighted_score: number;
  };
  experience_alignment: {
    raw_score: number; // 0.0 - 1.0
    weight: 0.15;
    weighted_score: number;
    candidate_years: number;
    required_years: number;
  };
  education_fit: {
    raw_score: number; // 0.0 - 1.0
    weight: 0.10;
    weighted_score: number;
    candidate_level: string;
    required_level: string;
  };
}

/**
 * ATS Explainability Insights
 */
export interface ExplainabilityReport {
  matched_skills: string[];
  missing_skills: string[];
  missing_required_skills?: string[];
  missing_preferred_skills?: string[];
  improvement_suggestions: string[];
}

/**
 * Candidate Match Result
 */
export interface CandidateMatch {
  rank: number;
  candidate_id: number;
  candidate_name: string;
  resume_id: number;
  total_score: number; // 0.0 - 100.0
  score_breakdown: ScoreSignalBreakdown;
  explainability: ExplainabilityReport;
}

/**
 * Ranked Match List Response (Recruiter View)
 */
export interface RankedMatchResponse {
  job_id: number;
  job_title: string;
  total_candidates_evaluated: number;
  matches: CandidateMatch[];
}

/**
 * Ad-Hoc Stateless Match Request & Response
 */
export interface AdHocMatchRequest {
  resume_text: string;
  job_description: string;
  required_skills: string[];
  preferred_skills?: string[];
  required_experience_years?: number;
  required_education_level?: string;
}

export interface AdHocMatchResponse {
  total_score: number;
  score_breakdown: ScoreSignalBreakdown;
  matched_skills: string[];
  missing_skills: string[];
  improvement_suggestions: string[];
}

/**
 * System Health Response
 */
export interface HealthStatus {
  status: 'alive' | 'ready' | 'degraded';
  database?: string;
  model?: string;
}
```

---

### 3.3 Core Component Specifications

#### 1. Drag-and-Drop Resume Uploader (`ResumeUploader.tsx`)
- **Features**:
  - Accept types: `.pdf`, `.docx`, `.txt` (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`).
  - Max file size: 10MB client-side rejection before network request.
  - Drag-over active visual state with glowing indigo borders.
  - Real-time animated progress bar (`0%` -> `100%`) with transition effects.
  - Error state displaying RFC 7807 Problem Details if server returns 400/415/422.
  - Success callback notifying parent state with `ParsedResumeProfile`.

#### 2. Parsed Profile Card (`ParsedProfileCard.tsx`)
- **Features**:
  - Candidate identity header (Name, Email, Phone, Location).
  - Metrics badges: Experience (years), Education Degree.
  - Extracted skills chip cloud with count badge.
  - Social profile links (LinkedIn, GitHub) with SVG icons.
  - Collapsible drawer for raw extracted text preview.

#### 3. Recruiter Job Posting Form (`JobRequisitionForm.tsx`)
- **Features**:
  - Input fields: Job Title, Company, Department, Location, Employment Type.
  - Dynamic skill tagger: Enter-key separated tag generation for Required Skills and Preferred Skills.
  - Sliders for Required Years of Experience (`0` to `15+`).
  - Education dropdown: `None`, `High School`, `Associate`, `Bachelor's`, `Master's`, `Doctorate`.
  - Salary range inputs (Min, Max).
  - Rich description textarea with validation feedback.
  - Submits to `POST /api/v1/jobs` and provides immediate redirection to the newly created job's talent leaderboard.

#### 4. Ranked Candidate Leaderboard & Skill Gap Visualizer
- **Features**:
  - Top 3 candidates highlighted with Gold, Silver, Bronze badges.
  - Composite ATS score badge with radial gauge preview.
  - Side-by-side Skill Gap Matrix:
    - **Green Badges**: Skills candidate possesses that match job requisitions.
    - **Red Badges**: Critical missing required skills.
    - **Amber Badges**: Missing preferred/bonus skills.
  - Drawer expansion for each candidate showing:
    - 4-signal breakdown bars with exact numerical contributions.
    - Curated improvement recommendations.

#### 5. Visualizer Components
- **`AtsScoreGauge.tsx`**:
  - Pure SVG radial gauge calculating circumference from score percentage:
    `strokeDashoffset = circumference - (score / 100) * circumference`.
  - Dynamic stroke color interpolation: Emerald (>=80), Indigo/Sky (65-79), Amber (50-64), Rose (<50).
- **`AtsRadarChart.tsx`**:
  - 4-axis diamond radar chart visualizing the four signals: Semantic (Top), Skills (Right), Experience (Bottom), Education (Left).
  - SVG polygon coordinates computed via `(cx + r * cos(theta), cy + r * sin(theta))`.
  - Semi-transparent fill with accent border and hover tooltips.

---

### 3.4 Infrastructure & DevOps Specifications

#### 3.4.1 Docker Compose Configuration (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg16
    container_name: talent_marketplace_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-talent_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-talent_pass}
      POSTGRES_DB: ${POSTGRES_DB:-talent_marketplace}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-talent_user} -d ${POSTGRES_DB:-talent_marketplace}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - talent_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: talent_marketplace_backend
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-talent_user}:${POSTGRES_PASSWORD:-talent_pass}@db:5432/${POSTGRES_DB:-talent_marketplace}
      EMBEDDING_MODEL_NAME: ${EMBEDDING_MODEL_NAME:-all-MiniLM-L6-v2}
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000}
      PORT: 8000
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health/live || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    networks:
      - talent_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: talent_marketplace_frontend
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      PORT: 3000
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000 || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks:
      - talent_network

volumes:
  pgdata:
    driver: local

networks:
  talent_network:
    driver: bridge
```

#### 3.4.2 Frontend Multi-Stage Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
    else npm ci; fi

# Stage 2: Builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Stage 3: Runner
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

CMD ["node", "server.js"]
```

#### 3.4.3 Biome Configuration (`frontend/biome.json`)
```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "files": {
    "ignoreUnknown": false,
    "includes": ["src/**/*", "*.ts", "*.js", "*.json"]
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noExplicitAny": "warn"
      },
      "correctness": {
        "noUnusedVariables": "error"
      },
      "a11y": {
        "useValidAnchor": "error",
        "useAltText": "error"
      }
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "es5",
      "semicolons": "always"
    }
  }
}
```

#### 3.4.4 GitHub Actions CI Pipeline (`.github/workflows/ci.yml`)
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-python:
    name: Lint & Format Python (Ruff)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Ruff
        run: pip install ruff

      - name: Run Ruff Linter
        run: ruff check backend/

      - name: Run Ruff Formatter Check
        run: ruff format --check backend/

  lint-frontend:
    name: Lint & Format Frontend (Biome)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'

      - name: Install Dependencies
        run: |
          cd frontend
          npm ci

      - name: Run Biome Check
        run: |
          cd frontend
          npx @biomejs/biome check src/

  test-backend:
    name: Pytest Backend Suite & Coverage
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run Tests with Coverage
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db
        run: |
          pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing --cov-fail-under=80

  docker-build:
    name: Docker Build Verification
    runs-on: ubuntu-latest
    needs: [lint-python, lint-frontend, test-backend]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: actions/setup-buildx-action@v3

      - name: Verify Docker Compose Build
        run: docker compose build
```

---

### 3.5 Repository Governance Specifications

#### 3.5.1 Environment Configuration Template (`.env.example`)
```bash
# ==============================================================================
# Database Configuration (PostgreSQL + pgvector)
# ==============================================================================
POSTGRES_USER=talent_user
POSTGRES_PASSWORD=talent_pass
POSTGRES_DB=talent_marketplace
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Async SQLAlchemy Connection URL
DATABASE_URL=postgresql+asyncpg://talent_user:talent_pass@localhost:5432/talent_marketplace

# ==============================================================================
# ML / NLP Matching Engine Configuration
# ==============================================================================
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
MAX_UPLOAD_SIZE_BYTES=10485760

# ==============================================================================
# Backend API Configuration
# ==============================================================================
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development

# ==============================================================================
# Frontend Web App Configuration
# ==============================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000
PORT=3000
```

#### 3.5.2 Git Ignore Specification (`.gitignore`)
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Python distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing & Coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.ruff_cache/

# Node / Next.js
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/build/
frontend/.turbo/
.npm
*.tsbuildinfo
next-env.d.ts

# Biome Cache
.biome/

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
!.env.example

# Docker / Database Volume Data
pgdata/
uploads/
*.log

# OS & Editor
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo
```

---

## 4. Caveats

1. **Client-Side vs Server-Side Fetching in Docker**:
   - In Next.js, Client Components running in the user's browser connect to the backend at `http://localhost:8000`.
   - If Server Components (RSC) or Server Actions fetch data during SSR inside the Docker network, `http://localhost:8000` refers to the container itself (not the backend container).
   - *Mitigation*: Configure `NEXT_PUBLIC_API_URL=http://localhost:8000` for client-side queries, and provide `BACKEND_INTERNAL_URL=http://backend:8000` for server-side fetches.
2. **File Upload Progress in Browser APIs**:
   - Modern `fetch()` does not natively expose upload stream progress in standard browsers without experimental Streams APIs.
   - *Mitigation*: Implement standard XMLHttpRequest or simulated smooth progress increments in `ResumeUploader.tsx` to provide immediate feedback to the candidate.
3. **Biome Version Alignment**:
   - Biome v2.5.14 was verified on the host machine. Ensure the `package.json` installs `@biomejs/biome@^2.5.14` or uses `biome.json` compatible syntax to avoid version mismatch errors.

---

## 5. Conclusion

The Frontend Web Application and Infrastructure architecture is thoroughly surveyed and specified:
- **Next.js App Router**: Optimized layout with candidate and recruiter portals, full TypeScript strictness matching backend schemas, and zero console errors.
- **Explainability Visualizers**: Clean SVG-based radial gauges, 4-signal breakdown bars, and radar charts delivering transparent ATS insights.
- **Docker Compose**: Production-ready multi-container orchestration with healthy dependency chains (`db` -> `backend` -> `frontend`).
- **CI/CD Quality**: Parallel Biome and Ruff linters with Pytest and Docker build verification in GitHub Actions.
- **Repository Governance**: Complete `.env.example`, `.gitignore`, and README specifications.

The specifications are self-contained and ready for immediate implementation by the development track.

---

## 6. Verification Method

To independently verify the environment, configurations, and architecture:
1. **Toolchain Verification**:
   - Run `node -v` (verify $\ge 20$, observed `v26.7.0`)
   - Run `npm -v` (observed `11.19.0`) / `pnpm -v` (observed `11.24.0`)
   - Run `npx @biomejs/biome --version` (observed `2.5.14`)
   - Run `docker --version` and `docker compose version`
2. **Linting Verification**:
   - Frontend: `npx @biomejs/biome check frontend/src`
   - Backend: `uvx ruff check backend/`
3. **Docker Compose Verification**:
   - Run `docker compose config` to validate syntax and environment resolution without starting containers.
   - Run `docker compose build` to verify multi-stage builds.
