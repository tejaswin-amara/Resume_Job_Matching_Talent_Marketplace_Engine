from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import HealthResponse
from db.session import get_db_session

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def live():
    return {"status": "ok"}


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"description": "Database unavailable"}},
)
async def ready(db: AsyncSession = Depends(get_db_session)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e

