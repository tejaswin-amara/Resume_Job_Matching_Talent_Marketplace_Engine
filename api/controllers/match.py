from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.errors import ProblemDetailException
from api.schemas import MatchResultResponse
from core.scoring.matcher import HybridMatcher
from db.models import (
    Candidate,
    CandidateSkill,
    JobPosting,
    JobSkillRequirement,
    MatchResult,
)
from db.session import get_db_session

router = APIRouter(prefix="/api/v1/match", tags=["match"])


class AdhocMatchRequest(BaseModel):
    candidate_id: UUID
    job_id: UUID


@router.post("/adhoc", response_model=MatchResultResponse)
async def adhoc_match(
    req: AdhocMatchRequest, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    cand = await db.get(
        Candidate,
        req.candidate_id,
        options=[selectinload(Candidate.skills).selectinload(CandidateSkill.skill)],
    )
    job = await db.get(
        JobPosting,
        req.job_id,
        options=[selectinload(JobPosting.skills).selectinload(JobSkillRequirement.skill)],
    )

    if not cand or not job:
        raise ProblemDetailException(404, "Not Found", "Candidate or Job not found")

    cand_skills = {cs.skill.name for cs in cand.skills}
    job_skills = {js.skill.name for js in job.skills}

    matcher = HybridMatcher()
    res = matcher.match(
        cand_emb=cand.embedding,
        job_emb=job.embedding,
        cand_skills=cand_skills,
        job_skills=job_skills,
        cand_exp=cand.total_experience_years,
        job_min_exp=job.min_experience,
    )

    db_match = MatchResult(
        candidate_id=cand.id,
        job_id=job.id,
        semantic_score=res.semantic_score,
        skill_score=res.skill_score,
        experience_score=res.experience_score,
        education_score=res.education_score,
        total_score=res.total_score,
        matched_skills=res.matched_skills,
        missing_skills=res.missing_skills,
        suggestions=res.suggestions,
    )
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)

    return db_match
