import asyncio
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.parsers.factory import ParserFactory
from core.scoring.embeddings import EmbeddingService
from core.scoring.skill_extractor import SkillExtractor
from db.models import Candidate, CandidateSkill, Skill
from db.session import get_db_session

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Dummy Firebase verification
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid auth credentials")
    return credentials.credentials


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(verify_token),
):
    content = await file.read()
    parser = ParserFactory.from_content_type(
        file.content_type or "application/octet-stream", content
    )

    try:
        text = await asyncio.to_thread(parser.parse, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    emb_service = EmbeddingService()
    embedding = await asyncio.to_thread(emb_service.encode, text)

    extractor = SkillExtractor()
    found_skills = await asyncio.to_thread(extractor.extract, text)

    import re

    # Simple extraction heuristic for email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0) if email_match else f"unknown_{uuid.uuid4().hex[:8]}@example.com"

    candidate = Candidate(
        name=file.filename or "Unknown",
        email=email,
        raw_text=text,
        embedding=embedding,
    )
    db.add(candidate)
    await db.flush()

    for s in found_skills:
        result = await db.execute(select(Skill).where(Skill.name == s))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=s)
            db.add(skill)
            await db.flush()

        db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))

    await db.commit()
    return {"id": str(candidate.id), "skills": list(found_skills), "raw_text": text}


class ParseTextRequest(BaseModel):
    text: str


@router.post("/parse-text")
async def parse_text(req: ParseTextRequest):
    extractor = SkillExtractor()
    skills = await asyncio.to_thread(extractor.extract, req.text)
    return {"skills": list(skills)}
