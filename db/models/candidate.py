import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    total_experience_years: Mapped[float] = mapped_column(Float, default=0.0)
    education_level: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    embedding = mapped_column(Vector(384))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    skills = relationship(
        "CandidateSkill", back_populates="candidate", cascade="all, delete-orphan"
    )
    match_results = relationship(
        "MatchResult", back_populates="candidate", cascade="all, delete-orphan"
    )
