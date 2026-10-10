import asyncio
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from api.schemas import MatchResultResponse
from core.scoring.embeddings import EmbeddingService
from core.scoring.matcher import HybridMatcher
from core.scoring.skill_extractor import SkillExtractor

router = APIRouter(prefix="/api/v1/match", tags=["match"])


class AdhocMatchRequest(BaseModel):
    resume_text: str
    job_description: str


@router.post("/adhoc", response_model=MatchResultResponse)
async def adhoc_match(req: AdhocMatchRequest):
    extractor = SkillExtractor()
    cand_skills_list = await asyncio.to_thread(extractor.extract, req.resume_text)
    job_skills_list = await asyncio.to_thread(extractor.extract, req.job_description)

    cand_skills = set(cand_skills_list)
    job_skills = set(job_skills_list)

    emb_service = EmbeddingService()
    cand_emb = await asyncio.to_thread(emb_service.encode, req.resume_text)
    job_emb = await asyncio.to_thread(emb_service.encode, req.job_description)

    matcher = HybridMatcher()
    res = await asyncio.to_thread(
        matcher.match,
        cand_emb=cand_emb,
        job_emb=job_emb,
        cand_skills=cand_skills,
        job_skills=job_skills,
        cand_exp=0.0,
        job_min_exp=0.0,
    )

    # Do not save to DB for adhoc match.
    return MatchResultResponse(
        candidate_id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        semantic_score=res.semantic_score,
        skill_score=res.skill_score,
        experience_score=res.experience_score,
        education_score=res.education_score,
        total_score=res.total_score,
        matched_skills=res.matched_skills,
        missing_skills=res.missing_skills,
        suggestions=res.suggestions,
    )
