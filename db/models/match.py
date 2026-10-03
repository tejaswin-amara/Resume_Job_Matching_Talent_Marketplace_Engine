import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False
    )

    semantic_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    education_score: Mapped[float] = mapped_column(Float, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)

    matched_skills: Mapped[dict] = mapped_column(JSONB, default=list)
    missing_skills: Mapped[dict] = mapped_column(JSONB, default=list)
    suggestions: Mapped[dict] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    candidate = relationship("Candidate", back_populates="match_results")
    job = relationship("JobPosting", back_populates="match_results")
