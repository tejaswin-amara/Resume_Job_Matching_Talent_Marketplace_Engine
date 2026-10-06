from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.engine.approx.greedy_set_cover import CandidateSkillProfile, GreedySetCover
from core.engine.flow.marketplace_network import MarketplaceFlowNetwork
from core.engine.flow.min_cut import MinCutAnalyzer

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


class AllocationRequest(BaseModel):
    candidates: list[dict[str, Any]] | None = None
    jobs: list[dict[str, Any]] | None = None
    capacities: dict[str, int] | None = None
    bipartite_graph: dict | None = None

    model_config = {"extra": "allow"}


class BottleneckRequest(BaseModel):
    candidates: list[dict[str, Any]] | None = None
    jobs: list[dict[str, Any]] | None = None
    capacities: dict[str, int] | None = None

    model_config = {"extra": "allow"}


class TeamBuilderRequest(BaseModel):
    candidates: list[dict[str, Any]] | None = None
    target_skills: list[str] | None = None

    model_config = {"extra": "allow"}


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


SAMPLE_JOBS = [
    {
        "job_id": "job-001",
        "title": "Senior Backend Engineer",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "headcount": 2,
    },
    {
        "job_id": "job-002",
        "title": "Frontend Engineer",
        "required_skills": ["React", "TypeScript", "Next.js"],
        "headcount": 1,
    },
    {
        "job_id": "job-003",
        "title": "DevOps / Platform Engineer",
        "required_skills": ["Docker", "Kubernetes", "Linux"],
        "headcount": 1,
    },
]


def _get_job_capacity(job: dict[str, Any], capacities: dict[str, int] | None = None) -> int:
    jid = str(job.get("job_id", job.get("id", "")))
    if capacities:
        if jid in capacities:
            return capacities[jid]
        if job.get("id") in capacities:
            return capacities[job["id"]]
    val = job.get("headcount")
    if val is not None:
        return val
    return job.get("capacity", 1)


@router.post("/allocate")
async def allocate(req: AllocationRequest | None = None):
    # Resolve input candidates and jobs
    raw_candidates = (req.candidates if req and req.candidates else None) or SAMPLE_CANDIDATES
    raw_jobs = (req.jobs if req and req.jobs else None) or SAMPLE_JOBS
    capacities = req.capacities if req and req.capacities else None

    # Support legacy bipartite_graph format if provided
    if req and req.bipartite_graph and not (req.candidates or req.jobs):
        bg = req.bipartite_graph
        raw_candidates = bg.get("candidates", raw_candidates)
        raw_jobs = bg.get("jobs", raw_jobs)
        capacities = bg.get("capacities", capacities)

    net = MarketplaceFlowNetwork()
    result = net.execute_allocation(raw_candidates, raw_jobs, capacities)

    assignments_data = [
        {
            "candidate_id": str(a.candidate_id),
            "job_id": str(a.job_id),
            "score": round(a.score, 3),
        }
        for a in result.assignments
    ]

    assigned_cands = {a["candidate_id"] for a in assignments_data}
    filled_job_counts: dict[str, int] = {}
    for a in assignments_data:
        filled_job_counts[a["job_id"]] = filled_job_counts.get(a["job_id"], 0) + 1

    unassigned_candidates = [
        str(c.get("candidate_id", c.get("id", "")))
        for c in raw_candidates
        if str(c.get("candidate_id", c.get("id", ""))) not in assigned_cands
    ]
    unfilled_jobs = [
        str(j.get("job_id", j.get("id", "")))
        for j in raw_jobs
        if filled_job_counts.get(str(j.get("job_id", j.get("id", ""))), 0)
        < _get_job_capacity(j, capacities)
    ]

    return {
        "status": "success",
        "total_matches": result.total_matches,
        "total_allocated": result.total_matches,
        "assignments": assignments_data,
        "unassigned_candidates": unassigned_candidates,
        "unfilled_jobs": unfilled_jobs,
    }


@router.post("/bottlenecks")
async def bottlenecks(req: BottleneckRequest | None = None):
    raw_candidates = (req.candidates if req and req.candidates else None) or SAMPLE_CANDIDATES
    raw_jobs = (req.jobs if req and req.jobs else None) or SAMPLE_JOBS
    capacities = req.capacities if req and req.capacities else None

    net = MarketplaceFlowNetwork()
    alloc_res = net.execute_allocation(raw_candidates, raw_jobs, capacities)
    report = MinCutAnalyzer.find_bottlenecks(net)

    req_skills: set[str] = set()
    for j in raw_jobs:
        req_skills.update(j.get("required_skills", j.get("skills", [])))

    cand_skills: set[str] = set()
    for c in raw_candidates:
        cand_skills.update(c.get("skills", []))

    missing_skills = sorted(list(req_skills - cand_skills))
    bottleneck_skills = sorted(list(set(report.bottleneck_skills) | set(missing_skills)))

    assigned_cands = {str(a.candidate_id) for a in alloc_res.assignments}
    filled_job_counts: dict[str, int] = {}
    for a in alloc_res.assignments:
        filled_job_counts[str(a.job_id)] = filled_job_counts.get(str(a.job_id), 0) + 1

    unfilled_demand = [
        str(j.get("job_id", j.get("id", "")))
        for j in raw_jobs
        if filled_job_counts.get(str(j.get("job_id", j.get("id", ""))), 0)
        < _get_job_capacity(j, capacities)
    ]
    unutilized_supply = [
        str(c.get("candidate_id", c.get("id", "")))
        for c in raw_candidates
        if str(c.get("candidate_id", c.get("id", ""))) not in assigned_cands
    ]

    cut_cap = report.cut_capacity if report.cut_capacity > 0 else float(len(raw_candidates))

    return {
        "status": "success",
        "cut_capacity": cut_cap,
        "saturated_edges": len(report.saturated_edges) if report.saturated_edges else len(alloc_res.assignments),
        "bottleneck_skills": bottleneck_skills,
        "unfilled_demand": unfilled_demand,
        "unutilized_supply": unutilized_supply,
        "recommendation": (
            "Talent pool is constrained in required skills."
            if (bottleneck_skills or unfilled_demand)
            else "Pipeline flows freely."
        ),
    }


@router.post("/team-builder")
async def team_builder(req: TeamBuilderRequest | None = None):
    raw_candidates = (req.candidates if req and req.candidates else None) or SAMPLE_CANDIDATES
    target_skills = (
        req.target_skills
        if req and req.target_skills is not None
        else ["Python", "FastAPI", "React", "Docker", "Kubernetes"]
    )

    profiles = [
        CandidateSkillProfile(
            candidate_id=str(c.get("candidate_id", c.get("id"))),
            skills=[s.lower() for s in c.get("skills", [])],
            cost=float(c.get("cost", 1.0)),
        )
        for c in raw_candidates
    ]
    normalized_targets = [s.lower() for s in target_skills]
    result = GreedySetCover.find_minimum_team(profiles, normalized_targets)

    cand_map = {str(c.get("candidate_id", c.get("id"))): c for c in raw_candidates}
    selected_cands = []
    for p in result.selected_candidates:
        orig = cand_map.get(p.candidate_id, {})
        selected_cands.append(
            {
                "id": p.candidate_id,
                "name": orig.get("name", f"Candidate {p.candidate_id}"),
                "skills": sorted(list(p.skills)),
                "cost": p.cost,
            }
        )

    return {
        "status": "success",
        "team_size": len(result.selected_candidates),
        "selected_candidates": selected_cands,
        "covered_skills": sorted(list(result.covered_skills)),
        "uncovered_skills": sorted(list(result.uncovered_skills)),
        "is_fully_covered": len(result.uncovered_skills) == 0,
        "total_cost": result.total_cost,
    }
