from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors import ProblemDetailException
from api.schemas import JobCreate, JobResponse
from core.scoring.embeddings import EmbeddingService
from db.models import JobPosting, JobSkillRequirement, Skill
from db.session import get_db_session

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db_session)):
    emb_service = EmbeddingService()
    text = f"{job_in.title} {job_in.description} {job_in.requirements}"
    embedding = emb_service.encode(text)

    job = JobPosting(
        title=job_in.title,
        department=job_in.department,
        description=job_in.description,
        requirements=job_in.requirements,
        min_experience=job_in.min_experience,
        max_experience=job_in.max_experience,
        location=job_in.location,
        headcount=job_in.headcount,
        embedding=embedding,
    )
    db.add(job)
    await db.flush()

    for s in job_in.skills:
        result = await db.execute(select(Skill).where(Skill.name == s.lower()))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=s.lower())
            db.add(skill)
            await db.flush()
        db.add(JobSkillRequirement(job_id=job.id, skill_id=skill.id))

    await db.commit()
    await db.refresh(job)
    return job


@router.get("", response_model=list[JobResponse])
async def list_jobs(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(JobPosting).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{id}/matches")
async def get_job_matches(id: UUID, db: AsyncSession = Depends(get_db_session)):
    job = await db.get(JobPosting, id)
    if not job:
        raise ProblemDetailException(404, "Not Found", "Job posting not found")

    # In a real app, this would query MatchResult
    return []
