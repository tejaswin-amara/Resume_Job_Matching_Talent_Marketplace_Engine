from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.controllers import health, jobs, marketplace, match, resumes
from api.errors import (
    ProblemDetailException,
    general_exception_handler,
    http_exception_handler,
    problem_detail_handler,
    validation_exception_handler,
)
from api.telemetry.tracing import setup_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    from db.session import close_db_engine

    await close_db_engine()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
setup_telemetry(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ProblemDetailException, problem_detail_handler)  # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(Exception, general_exception_handler)  # type: ignore

app.include_router(health.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(marketplace.router)
app.include_router(match.router)
