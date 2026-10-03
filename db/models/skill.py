import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True
    )
    proficiency_weight: Mapped[float] = mapped_column(Float, default=1.0)

    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill")
