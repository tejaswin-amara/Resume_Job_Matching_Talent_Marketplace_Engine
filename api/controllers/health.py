from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def live():
    return {"status": "ok"}


@router.get("/ready", response_model=HealthResponse)
async def ready():
    # In a real app, check DB connection here
    return {"status": "ready"}
