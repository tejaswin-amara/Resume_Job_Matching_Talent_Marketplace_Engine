from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


class AllocationRequest(BaseModel):
    bipartite_graph: dict


class CandidateMatchItem(BaseModel):
    candidate_id: str
    name: str | None = None
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    experience_years: int


class RecruiterMatchRequest(BaseModel):
    job_id: str | None = None
    title: str = "Senior Full Stack Engineer"
    required_skills: list[str] = Field(
        default_factory=lambda: ["Python", "FastAPI", "React", "PostgreSQL"]
    )
    min_experience: int = 4
    candidate_limit: int = 10


class RecruiterMatchResponse(BaseModel):
    status: str = "success"
    job_id: str | None = None
    total_candidates: int
    matches: list[CandidateMatchItem]


SAMPLE_CANDIDATES = [
    {
        "candidate_id": "cand-001",
        "name": "Alex Mercer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "pgvector", "Docker", "React"],
        "experience_years": 6,
    },
    {
        "candidate_id": "cand-002",
        "name": "Sarah Connor",
        "skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "experience_years": 5,
    },
    {
        "candidate_id": "cand-003",
        "name": "David Bowman",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
        "experience_years": 4,
    },
    {
        "candidate_id": "cand-004",
        "name": "Elena Rostova",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
        "experience_years": 7,
    },
    {
        "candidate_id": "cand-005",
        "name": "Marcus Vance",
        "skills": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"],
        "experience_years": 8,
    },
    {
        "candidate_id": "cand-006",
        "name": "Chloe Sullivan",
        "skills": ["React", "Vue", "CSS", "HTML", "JavaScript"],
        "experience_years": 3,
    },
    {
        "candidate_id": "cand-007",
        "name": "Kenji Sato",
        "skills": ["Python", "PostgreSQL", "C++", "Linux", "FastAPI"],
        "experience_years": 4,
    },
]


@router.post("/match", response_model=RecruiterMatchResponse)
async def marketplace_match(req: RecruiterMatchRequest) -> RecruiterMatchResponse:
    req_skills_lower = {s.lower(): s for s in req.required_skills}
    computed_matches: list[CandidateMatchItem] = []

    for candidate in SAMPLE_CANDIDATES:
        cand_skills_lower = {s.lower() for s in candidate["skills"]}
        matched = [
            req_skills_lower[k]
            for k in req_skills_lower
            if k in cand_skills_lower
        ]
        missing = [
            req_skills_lower[k]
            for k in req_skills_lower
            if k not in cand_skills_lower
        ]

        total_req = max(len(req.required_skills), 1)
        skill_score = (len(matched) / total_req) * 100.0
        exp_ratio = candidate["experience_years"] / max(req.min_experience, 1)
        exp_score = min(100.0, exp_ratio * 100.0)
        composite_score = round(0.70 * skill_score + 0.30 * exp_score, 1)

        computed_matches.append(
            CandidateMatchItem(
                candidate_id=candidate["candidate_id"],
                name=candidate["name"],
                score=composite_score,
                matched_skills=matched,
                missing_skills=missing,
                experience_years=candidate["experience_years"],
            )
        )

    computed_matches.sort(key=lambda m: m.score, reverse=True)
    selected_matches = computed_matches[: req.candidate_limit]

    return RecruiterMatchResponse(
        status="success",
        job_id=req.job_id or "job-req-001",
        total_candidates=len(selected_matches),
        matches=selected_matches,
    )


@router.post("/allocate")
async def allocate(req: AllocationRequest):
    # Wrapper around core.engine.graph.dinics
    return {"message": "Dinic's allocation not fully wired up yet"}


@router.post("/bottlenecks")
async def bottlenecks():
    return {"message": "Min-Cut bottlenecks"}


@router.post("/team-builder")
async def team_builder():
    return {"message": "Set Cover team builder"}
