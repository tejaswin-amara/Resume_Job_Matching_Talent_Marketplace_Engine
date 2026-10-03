"""Initial schema with pgvector and all talent marketplace tables.

Revision ID: 20260930_0001
Revises: None
Create Date: 2026-09-30 15:30:00.000000
"""
from collections.abc import Sequence

import pgvector
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260930_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Skills table
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("category", sa.String(), nullable=True),
    )

    # 3. Candidates table
    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("total_experience_years", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("education_level", sa.String(), nullable=True),
        sa.Column("raw_text", sa.String(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 4. CandidateSkills table
    op.create_table(
        "candidate_skills",
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "skill_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("proficiency_weight", sa.Float(), server_default="1.0", nullable=False),
    )

    # 5. JobPostings table
    op.create_table(
        "job_postings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("requirements", sa.String(), nullable=False),
        sa.Column("min_experience", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("max_experience", sa.Float(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("headcount", sa.Integer(), server_default="1", nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 6. JobSkillRequirements table
    op.create_table(
        "job_skill_requirements",
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("job_postings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "skill_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("is_required", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("weight", sa.Float(), server_default="1.0", nullable=False),
    )

    # 7. MatchResults table
    op.create_table(
        "match_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("job_postings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("semantic_score", sa.Float(), nullable=False),
        sa.Column("skill_score", sa.Float(), nullable=False),
        sa.Column("experience_score", sa.Float(), nullable=False),
        sa.Column("education_score", sa.Float(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("matched_skills", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("missing_skills", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("suggestions", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("match_results")
    op.drop_table("job_skill_requirements")
    op.drop_table("job_postings")
    op.drop_table("candidate_skills")
    op.drop_table("candidates")
    op.drop_table("skills")
    op.execute("DROP EXTENSION IF EXISTS vector;")
