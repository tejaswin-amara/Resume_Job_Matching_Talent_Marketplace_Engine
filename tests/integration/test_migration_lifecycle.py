import asyncio

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

try:
    from testcontainers.community.postgres import PostgresContainer
except ImportError:
    from testcontainers.postgres import PostgresContainer

from api.config import settings


def is_docker_available() -> bool:
    try:
        import docker
        from testcontainers.core.container import DockerContainer

        client = docker.from_env()
        client.ping()
        try:
            with DockerContainer("alpine:latest").with_command("echo 1"):
                pass
        except Exception:
            return False
        return True
    except Exception:
        return False


@pytest.mark.skipif(not is_docker_available(), reason="Docker daemon unavailable")
@pytest.mark.asyncio
async def test_migration_lifecycle_upgrade_downgrade_reupgrade(monkeypatch):
    """Verify clean upgrade, downgrade, and re-upgrade without pre-installing pgvector."""
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
        # Override the database URL with the Testcontainers DB
        db_url = postgres.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")

        # 1. First Upgrade to Head
        alembic_cfg = Config("alembic.ini")
        monkeypatch.setattr(settings, "database_url", db_url)

        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

        engine = create_async_engine(db_url, poolclass=NullPool)

        # 2. Verify schema exists and pgvector is installed
        async with engine.begin() as conn:
            # check candidates table
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'candidates')"
                )
            )
            assert result.scalar() is True

            # check extension
            ext_res = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            assert ext_res.scalar() == "vector"

        # 3. Downgrade to Base
        await asyncio.to_thread(command.downgrade, alembic_cfg, "base")

        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'candidates')"
                )
            )
            assert result.scalar() is False

        # 4. Re-Upgrade to Head
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'candidates')"
                )
            )
            assert result.scalar() is True

        await engine.dispose()
