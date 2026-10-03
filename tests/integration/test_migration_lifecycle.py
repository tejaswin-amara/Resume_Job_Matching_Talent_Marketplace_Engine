"""Adversarial test for database migrations and schema verification."""

import asyncio
import os
import pytest
import docker
from alembic import command
from alembic.config import Config
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine

try:
    from testcontainers.community.postgres import PostgresContainer
except ImportError:
    from testcontainers.postgres import PostgresContainer

from api.config import settings

def is_docker_available() -> bool:
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False

@pytest.mark.skipif(not is_docker_available(), reason="Docker daemon unavailable")
@pytest.mark.asyncio
async def test_migration_lifecycle_upgrade_downgrade_reupgrade():
    """Verify clean upgrade, downgrade, and re-upgrade without pre-installing pgvector."""
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        user = postgres.username
        password = postgres.password
        dbname = postgres.dbname

        async_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
        os.environ["DATABASE_URL"] = async_url
        settings.database_url = async_url

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", async_url)

        # 1. Test clean upgrade directly (no manual CREATE EXTENSION beforehand)
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

        engine = create_async_engine(async_url)
        async with engine.connect() as conn:
            # Verify extension 'vector' is installed
            res = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            ext = res.scalar()
            assert ext == "vector", f"Expected 'vector' extension, got {ext}"

            # Verify all 6 tables exist
            res = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
            ))
            tables = set(res.scalars().all())
            expected_tables = {
                "alembic_version",
                "skills",
                "candidates",
                "candidate_skills",
                "job_postings",
                "job_skill_requirements",
                "match_results",
            }
            assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

            # Verify embedding column type in candidates and job_postings
            for t in ["candidates", "job_postings"]:
                res = await conn.execute(text(f"""
                    SELECT udt_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{t}' AND column_name = 'embedding';
                """))
                row = res.fetchone()
                assert row is not None, f"No embedding column in {t}"
                assert row[0] == "vector" or "USER-DEFINED" in row[1]

            # Verify foreign key cascade constraints
            res = await conn.execute(text("""
                SELECT tc.table_name, kcu.column_name, rc.delete_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.referential_constraints AS rc
                  ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY';
            """))
            fks = res.fetchall()
            for fk in fks:
                assert fk[2] == "CASCADE", f"FK {fk[0]}.{fk[1]} is not CASCADE"

        # 2. Test downgrade to base
        await asyncio.to_thread(command.downgrade, alembic_cfg, "base")

        async with engine.connect() as conn:
            res = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
            ))
            remaining_tables = set(res.scalars().all()) - {"alembic_version"}
            assert len(remaining_tables) == 0, f"Tables not dropped: {remaining_tables}"

            res = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            ext = res.scalar()
            assert ext is None, "vector extension was not dropped on downgrade"

        # 3. Test re-upgrade
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            assert res.scalar() == "vector"

        await engine.dispose()
