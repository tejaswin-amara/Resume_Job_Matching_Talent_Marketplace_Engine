from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.engine.approx.greedy_set_cover import CandidateSkillProfile, GreedySetCover
from core.engine.flow.marketplace_network import MarketplaceFlowNetwork
from core.engine.flow.min_cut import MinCutAnalyzer
from db.models import Candidate, CandidateSkill, JobPosting, JobSkillRequirement
from db.session import get_db_session

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Dummy Firebase verification
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid auth credentials")
    return credentials.credentials


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


@router.post("/match", response_model=RecruiterMatchResponse)
async def marketplace_match(
    req: RecruiterMatchRequest, db: AsyncSession = Depends(get_db_session)
) -> RecruiterMatchResponse:
    result = await db.execute(
        select(Candidate).options(
            selectinload(Candidate.skills).selectinload(CandidateSkill.skill)
        )
    )
    candidates = result.scalars().all()
    db_candidates = [
        {
            "candidate_id": str(c.id),
            "name": c.name,
            "skills": [s.skill.name for s in c.skills if s.skill],
            "experience_years": c.total_experience_years,
        }
        for c in candidates
    ]
    req_skills_lower = {s.lower(): s for s in req.required_skills}
    computed_matches: list[CandidateMatchItem] = []

    for candidate in db_candidates:
        c_skills: list[str] = candidate.get("skills", [])  # type: ignore
        c_exp: float = float(candidate.get("experience_years", 0.0))  # type: ignore
        cand_skills_lower = {s.lower() for s in c_skills}
        matched = [req_skills_lower[k] for k in req_skills_lower if k in cand_skills_lower]
        missing = [req_skills_lower[k] for k in req_skills_lower if k not in cand_skills_lower]

        total_req = max(len(req.required_skills), 1)
        skill_score = (len(matched) / total_req) * 100.0
        exp_ratio = c_exp / max(req.min_experience, 1)
        exp_score = min(100.0, exp_ratio * 100.0)
        composite_score = round(0.70 * skill_score + 0.30 * exp_score, 1)

        computed_matches.append(
            CandidateMatchItem(
                candidate_id=str(candidate["candidate_id"]),
                name=str(candidate["name"]) if candidate.get("name") else None,
                score=composite_score,
                matched_skills=matched,
                missing_skills=missing,
                experience_years=int(c_exp),
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


def _get_job_capacity(job: dict[str, Any], capacities: dict[str, int] | None = None) -> int:
    jid = str(job.get("job_id", job.get("id", "")))
    if capacities:
        if jid in capacities:
            return capacities[jid]
        job_id_obj = job.get("id")
        if job_id_obj is not None and str(job_id_obj) in capacities:
            return capacities[str(job_id_obj)]
    val = job.get("headcount")
    if val is not None:
        return val
    return job.get("capacity", 1)


@router.post("/allocate")
async def allocate(
    req: AllocationRequest | None = None, db: AsyncSession = Depends(get_db_session)
):
    # Resolve input candidates and jobs
    if req and req.candidates:
        raw_candidates = req.candidates
    else:
        result_c = await db.execute(
            select(Candidate).options(
                selectinload(Candidate.skills).selectinload(CandidateSkill.skill)
            )
        )
        raw_candidates = [
            {
                "candidate_id": str(c.id),
                "name": c.name,
                "skills": [s.skill.name for s in c.skills if s.skill],
                "experience_years": c.total_experience_years,
            }
            for c in result_c.scalars().all()
        ]

    if req and req.jobs:
        raw_jobs = req.jobs
    else:
        result_j = await db.execute(
            select(JobPosting).options(
                selectinload(JobPosting.skills).selectinload(JobSkillRequirement.skill)
            )
        )
        raw_jobs = [
            {
                "job_id": str(j.id),
                "title": j.title,
                "required_skills": [s.skill.name for s in j.skills if s.skill],
                "headcount": j.headcount,
                "min_experience": j.min_experience,
            }
            for j in result_j.scalars().all()
        ]
    capacities = req.capacities if req and req.capacities else None

    # Support legacy bipartite_graph format if provided
    if req and req.bipartite_graph and not (req.candidates or req.jobs):
        bg = req.bipartite_graph
        raw_candidates = bg.get("candidates", raw_candidates)
        raw_jobs = bg.get("jobs", raw_jobs)
        capacities = bg.get("capacities", capacities)

    net = MarketplaceFlowNetwork()
    # Objective: Maximize total number of valid assignments (Maximum Cardinality)
    # Note: This does not optimize for maximum total score, only maximum filled positions.
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
        filled_job_counts[str(a["job_id"])] = filled_job_counts.get(str(a["job_id"]), 0) + 1

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
async def bottlenecks(
    req: BottleneckRequest | None = None, db: AsyncSession = Depends(get_db_session)
):
    if req and req.candidates:
        raw_candidates = req.candidates
    else:
        result_c = await db.execute(
            select(Candidate).options(
                selectinload(Candidate.skills).selectinload(CandidateSkill.skill)
            )
        )
        raw_candidates = [
            {
                "candidate_id": str(c.id),
                "name": c.name,
                "skills": [s.skill.name for s in c.skills if s.skill],
                "experience_years": c.total_experience_years,
            }
            for c in result_c.scalars().all()
        ]

    if req and req.jobs:
        raw_jobs = req.jobs
    else:
        result_j = await db.execute(
            select(JobPosting).options(
                selectinload(JobPosting.skills).selectinload(JobSkillRequirement.skill)
            )
        )
        raw_jobs = [
            {
                "job_id": str(j.id),
                "title": j.title,
                "required_skills": [s.skill.name for s in j.skills if s.skill],
                "headcount": j.headcount,
                "min_experience": j.min_experience,
            }
            for j in result_j.scalars().all()
        ]
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

    unfilled_demand = []
    for j in raw_jobs:
        job_id_str = str(j.get("job_id", j.get("id", "")))
        if filled_job_counts.get(job_id_str, 0) < int(_get_job_capacity(j, capacities)):
            unfilled_demand.append(job_id_str)
    unutilized_supply = [
        str(c.get("candidate_id", c.get("id", "")))
        for c in raw_candidates
        if str(c.get("candidate_id", c.get("id", ""))) not in assigned_cands
    ]

    cut_cap = report.cut_capacity if report.cut_capacity > 0 else float(len(raw_candidates))

    return {
        "status": "success",
        "cut_capacity": cut_cap,
        "saturated_edges": len(report.saturated_edges)
        if report.saturated_edges
        else len(alloc_res.assignments),
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
async def team_builder(
    req: TeamBuilderRequest | None = None, db: AsyncSession = Depends(get_db_session)
):
    if req and req.candidates:
        raw_candidates = req.candidates
    else:
        result_c = await db.execute(
            select(Candidate).options(
                selectinload(Candidate.skills).selectinload(CandidateSkill.skill)
            )
        )
        raw_candidates = [
            {
                "candidate_id": str(c.id),
                "name": c.name,
                "skills": [s.skill.name for s in c.skills if s.skill],
                "experience_years": c.total_experience_years,
            }
            for c in result_c.scalars().all()
        ]
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
