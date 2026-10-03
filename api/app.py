from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.controllers import health, jobs, marketplace, match, resumes
from api.errors import ProblemDetailException, problem_detail_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ProblemDetailException, problem_detail_handler)

app.include_router(health.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(marketplace.router)
app.include_router(match.router)
