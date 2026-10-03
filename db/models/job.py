import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    requirements: Mapped[str] = mapped_column(String, nullable=False)
    min_experience: Mapped[float] = mapped_column(Float, default=0.0)
    max_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    headcount: Mapped[int] = mapped_column(Integer, default=1)
    embedding = mapped_column(Vector(384))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    skills = relationship(
        "JobSkillRequirement", back_populates="job", cascade="all, delete-orphan"
    )
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")


class JobSkillRequirement(Base):
    __tablename__ = "job_skill_requirements"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    job = relationship("JobPosting", back_populates="skills")
    skill = relationship("Skill")
