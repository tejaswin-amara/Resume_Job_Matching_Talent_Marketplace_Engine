"""Integration test suite executing against pgvector/pgvector:pg16 container.

Tests:
1. Docker testcontainer spin-up with pgvector:pg16.
2. Alembic migration execution (creating tables + vector extension in worker thread).
3. Data insertion (Skills, Candidate, JobPosting with 384-dim vectors).
4. Native pgvector cosine similarity distance queries in PostgreSQL.
5. End-to-end HybridMatcher calculation and MatchResult persistence.
6. Nearest neighbor ordering query using pgvector index/distance.
7. Cascade deletion integrity across relational foreign keys.
"""

import asyncio
import os
import uuid

import docker
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

try:
    from testcontainers.community.postgres import PostgresContainer
except ImportError:
    from testcontainers.postgres import PostgresContainer

from api.config import settings
from core.scoring.matcher import HybridMatcher
from db.models import (
    Candidate,
    CandidateSkill,
    JobPosting,
    JobSkillRequirement,
    MatchResult,
    Skill,
)


def is_docker_available() -> bool:
    try:
        import docker
        from testcontainers.core.container import DockerContainer

        client = docker.from_env()
        client.ping()
        try:
            with DockerContainer("alpine:latest").with_command("echo 1"):
                pass
        except Exception as e:
            if "overlay" in str(e).lower() or "500 server error" in str(e).lower():
                return False
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not is_docker_available(), reason="Docker daemon unavailable")


@pytest.fixture(scope="module")
def postgres_pgvector_container():
    """Starts a testcontainers instance of pgvector/pgvector:pg16."""
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def db_urls(postgres_pgvector_container):
    host = postgres_pgvector_container.get_container_host_ip()
    port = postgres_pgvector_container.get_exposed_port(5432)
    user = postgres_pgvector_container.username
    password = postgres_pgvector_container.password
    dbname = postgres_pgvector_container.dbname

    async_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    sync_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return {"async_url": async_url, "sync_url": sync_url}


@pytest.fixture(scope="module")
async def migrated_db(db_urls):
    """Applies Alembic migrations against the testcontainer DB."""
    async_url = db_urls["async_url"]
    os.environ["DATABASE_URL"] = async_url
    settings.database_url = async_url

    # Ensure vector extension is present
    engine = create_async_engine(async_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    await engine.dispose()

    # Run Alembic upgrade head in thread to prevent event loop collision
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", async_url)
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    # Yield sessionmaker
    test_engine = create_async_engine(async_url, poolclass=NullPool, echo=False)
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    yield session_maker
    await test_engine.dispose()


async def _seed_candidate_and_job(
    session: AsyncSession,
) -> tuple[Candidate, JobPosting, Skill, Skill]:
    """Helper to seed candidate, job posting, and skill relations."""
    s_py = f"python_{uuid.uuid4().hex[:6]}"
    s_fa = f"fastapi_{uuid.uuid4().hex[:6]}"
    py_skill = Skill(id=uuid.uuid4(), name=s_py, category="Backend")
    fa_skill = Skill(id=uuid.uuid4(), name=s_fa, category="Backend")
    session.add_all([py_skill, fa_skill])
    await session.flush()

    cand_emb = [0.0] * 384
    cand_emb[0] = 1.0  # Unit vector on axis 0
    candidate = Candidate(
        id=uuid.uuid4(),
        name="Alice Backend Developer",
        email=f"alice_{uuid.uuid4().hex[:8]}@example.com",
        total_experience_years=5.0,
        education_level="bachelors",
        raw_text="Experienced Python FastAPI developer with 5 years experience.",
        embedding=cand_emb,
    )
    session.add(candidate)
    await session.flush()

    session.add_all(
        [
            CandidateSkill(candidate_id=candidate.id, skill_id=py_skill.id),
            CandidateSkill(candidate_id=candidate.id, skill_id=fa_skill.id),
        ]
    )

    job_emb = [0.0] * 384
    job_emb[0] = 0.95
    job_emb[1] = 0.3122498999199199  # sqrt(1 - 0.95^2), norm == 1.0
    job = JobPosting(
        id=uuid.uuid4(),
        title="Senior Python Backend Engineer",
        description="Build scalable APIs using Python and FastAPI",
        requirements="Python, FastAPI, PostgreSQL",
        min_experience=4.0,
        embedding=job_emb,
    )
    session.add(job)
    await session.flush()

    session.add_all(
        [
            JobSkillRequirement(job_id=job.id, skill_id=py_skill.id, is_required=True),
            JobSkillRequirement(job_id=job.id, skill_id=fa_skill.id, is_required=True),
        ]
    )
    await session.commit()
    return candidate, job, py_skill, fa_skill


@pytest.mark.asyncio
async def test_pgvector_and_hybrid_scoring_e2e(migrated_db):
    """Verifies pgvector cosine distance, HybridMatcher scoring, and persistence."""
    async with migrated_db() as session:
        candidate, job, py_skill, fa_skill = await _seed_candidate_and_job(session)

        # 4. Assert native pgvector cosine similarity calculation in PostgreSQL
        vector_str = "[" + ",".join(str(x) for x in job.embedding) + "]"
        query = text(
            "SELECT id, 1 - (embedding <=> :job_vec) AS cosine_similarity "
            "FROM candidates WHERE id = :cid"
        )
        result = await session.execute(query, {"job_vec": vector_str, "cid": candidate.id})
        row = result.fetchone()
        assert row is not None
        cosine_sim = float(row.cosine_similarity)
        assert 0.94 <= cosine_sim <= 0.96

        # Also verify via pgvector SQLAlchemy ORM operator
        orm_stmt = select(
            Candidate.id,
            (1 - Candidate.embedding.cosine_distance(job.embedding)).label("sim"),
        ).where(Candidate.id == candidate.id)
        orm_res = await session.execute(orm_stmt)
        orm_row = orm_res.fetchone()
        assert orm_row is not None
        assert 0.94 <= float(orm_row.sim) <= 0.96

        # 5. Execute HybridMatcher and verify formula
        matcher = HybridMatcher()
        match_output = matcher.match(
            cand_emb=candidate.embedding,
            job_emb=job.embedding,
            cand_skills={py_skill.name, fa_skill.name},
            job_skills={py_skill.name, fa_skill.name},
            cand_exp=candidate.total_experience_years,
            job_min_exp=job.min_experience,
            cand_edu="bachelors",
            job_req_edu="bachelors",
        )

        assert match_output.skill_score == 1.0
        assert match_output.experience_score == 1.0
        assert match_output.education_score == 1.0
        assert match_output.total_score >= 95.0

        # 6. Persist MatchResult and verify roundtrip retrieval
        db_match = MatchResult(
            candidate_id=candidate.id,
            job_id=job.id,
            semantic_score=match_output.semantic_score,
            skill_score=match_output.skill_score,
            experience_score=match_output.experience_score,
            education_score=match_output.education_score,
            total_score=match_output.total_score,
            matched_skills=match_output.matched_skills,
            missing_skills=match_output.missing_skills,
            suggestions=match_output.suggestions,
        )
        session.add(db_match)
        await session.commit()

        # Verify stored record
        stored = await session.get(MatchResult, db_match.id)
        assert stored is not None
        assert stored.total_score == match_output.total_score
        assert py_skill.name in stored.matched_skills
        assert fa_skill.name in stored.matched_skills


@pytest.mark.asyncio
async def test_pgvector_nearest_neighbor_ordering(migrated_db):
    """Verifies that pgvector ordering ranks closer candidate above distant candidate."""
    async with migrated_db() as session:
        # Candidate A: aligned vector
        cand_a_emb = [0.0] * 384
        cand_a_emb[0] = 1.0
        cand_a = Candidate(
            id=uuid.uuid4(),
            name="Aligned Candidate",
            email=f"cand_a_{uuid.uuid4().hex[:8]}@example.com",
            total_experience_years=3.0,
            raw_text="Aligned profile",
            embedding=cand_a_emb,
        )

        # Candidate B: orthogonal vector
        cand_b_emb = [0.0] * 384
        cand_b_emb[1] = 1.0
        cand_b = Candidate(
            id=uuid.uuid4(),
            name="Orthogonal Candidate",
            email=f"cand_b_{uuid.uuid4().hex[:8]}@example.com",
            total_experience_years=3.0,
            raw_text="Orthogonal profile",
            embedding=cand_b_emb,
        )

        session.add_all([cand_a, cand_b])
        await session.commit()

        # Target query vector pointing towards Candidate A
        query_vec = [0.0] * 384
        query_vec[0] = 0.99
        query_vec[1] = 0.141067  # unit vector

        stmt = (
            select(Candidate)
            .where(Candidate.id.in_([cand_a.id, cand_b.id]))
            .order_by(Candidate.embedding.cosine_distance(query_vec))
        )
        res = await session.execute(stmt)
        ranked = res.scalars().all()

        assert len(ranked) == 2
        assert ranked[0].id == cand_a.id
        assert ranked[1].id == cand_b.id


@pytest.mark.asyncio
async def test_cascade_delete_integrity(migrated_db):
    """Verifies CASCADE deletion integrity when candidate is removed."""
    async with migrated_db() as session:
        skill = Skill(id=uuid.uuid4(), name=f"skill_{uuid.uuid4().hex[:6]}")
        cand = Candidate(
            id=uuid.uuid4(),
            name="Temporary Candidate",
            email=f"temp_{uuid.uuid4().hex[:8]}@example.com",
            total_experience_years=2.0,
            raw_text="Temp profile",
            embedding=[0.0] * 384,
        )
        session.add_all([skill, cand])
        await session.flush()

        cs = CandidateSkill(candidate_id=cand.id, skill_id=skill.id)
        session.add(cs)
        await session.commit()

        # Delete candidate
        await session.delete(cand)
        await session.commit()

        # Verify candidate_skill row was cascade deleted
        check_cs = await session.get(CandidateSkill, (cand.id, skill.id))
        assert check_cs is None
