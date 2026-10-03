"""Pydantic v2 request/response schemas for the Talent Marketplace API."""

from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class JobCreate(BaseModel):
    """Job posting creation request."""

    title: str
    department: str | None = None
    description: str
    requirements: str
    min_experience: float = 0.0
    max_experience: float | None = None
    location: str | None = None
    headcount: int = 1
    skills: list[str] = Field(default_factory=list)


class JobResponse(JobCreate):
    """Job posting response with server-generated fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_at: datetime


class MatchResultResponse(BaseModel):
    """ATS match result with full score breakdown."""

    model_config = ConfigDict(from_attributes=True)

    candidate_id: UUID4
    job_id: UUID4
    total_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]


class CandidateCreate(BaseModel):
    """Candidate creation request."""

    name: str
    email: str
    phone: str | None = None
    total_experience_years: float = 0.0
    education_level: str | None = None
    raw_text: str


class CandidateResponse(CandidateCreate):
    """Candidate response with server-generated fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_at: datetime
