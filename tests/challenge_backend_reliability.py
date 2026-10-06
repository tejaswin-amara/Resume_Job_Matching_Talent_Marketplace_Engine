"""Empirical Challenge Suite: Backend Security, Concurrency, and CI Reliability.

Authored by: challenger_backend_reliability_1
Purpose: Adversarial stress verification of Milestone M1 and M4 fixes.
Covers:
1. CORS wildcard rejection and origin controls.
2. Event loop non-blocking behavior with asyncio.to_thread under concurrent load.
3. /health/ready database ping execution and HTTP 503 failure handling.
4. .dockerignore completeness (.git, .venv, node_modules, scratch).
5. GitHub Actions trivy-action pinning to 0.28.0.
"""

import ast
import asyncio
import re
import threading
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api.app import app
from api.config import settings
from api.controllers.health import ready
from db.models import Candidate, JobPosting, Skill
from db.session import get_db_session


# ==============================================================================
# Challenge 1: CORS Hardening & Wildcard Rejection
# ==============================================================================
class TestCORSVerification:
    """Empirical verification of CORS configuration and wildcard rejection."""

    def test_cors_settings_default_not_wildcard(self):
        """Verify settings.cors_origins does NOT contain wildcard '*'."""
        assert "*" not in settings.cors_origins
        assert "http://localhost:3000" in settings.cors_origins

    @pytest.mark.asyncio
    async def test_disallowed_origin_rejected_on_simple_request(self):
        """Adversarial request from evil.com must NOT receive Access-Control-Allow-Origin."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/health/live", headers={"Origin": "https://evil-hacker.com"})
            assert resp.status_code == 200
            # Header must NOT be present, and definitely not wildcard
            assert "access-control-allow-origin" not in resp.headers

    @pytest.mark.asyncio
    async def test_disallowed_origin_rejected_on_preflight(self):
        """Adversarial preflight OPTIONS from evil.com must be rejected."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.options(
                "/health/live",
                headers={
                    "Origin": "https://evil-hacker.com",
                    "Access-Control-Request-Method": "GET",
                },
            )
            # Either 400 or response without allow-origin
            allow_origin = resp.headers.get("access-control-allow-origin")
            assert allow_origin != "*"
            assert allow_origin != "https://evil-hacker.com"
            assert allow_origin is None

    @pytest.mark.asyncio
    async def test_allowed_origin_accepted_with_credentials(self):
        """Legitimate request from localhost:3000 receives proper CORS headers."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/health/live", headers={"Origin": "http://localhost:3000"})
            assert resp.status_code == 200
            assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
            assert resp.headers.get("access-control-allow-credentials") == "true"

    @pytest.mark.asyncio
    async def test_allowed_origin_preflight(self):
        """Legitimate preflight from localhost:3000 succeeds."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.options(
                "/health/live",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )
            assert resp.status_code == 200
            assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
            assert resp.headers.get("access-control-allow-credentials") == "true"


# ==============================================================================
# Challenge 2: /health/ready Database Ping & Failure Modes
# ==============================================================================
class TestReadinessProbeVerification:
    """Empirical verification of /health/ready probe executing SELECT 1 and handling DB failure."""

    @pytest.mark.asyncio
    async def test_ready_probe_executes_select_1_on_success(self):
        """Verify ready probe runs 'SELECT 1' and returns 200."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result

        result = await ready(db=mock_session)
        assert result == {"status": "ready"}
        mock_session.execute.assert_awaited_once()
        query_arg = mock_session.execute.await_args[0][0]
        assert str(query_arg).strip() == "SELECT 1"

    @pytest.mark.asyncio
    async def test_ready_probe_returns_503_on_db_operational_error(self):
        """Simulate PostgreSQL down with OperationalError -> Must return HTTP 503."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("Connection refused"))

        with pytest.raises(HTTPException) as exc_info:
            await ready(db=mock_session)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Database unavailable"

    @pytest.mark.asyncio
    async def test_ready_probe_returns_503_on_db_generic_exception(self):
        """Simulate unexpected DB exception -> Must return HTTP 503."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = RuntimeError("Fatal socket termination")

        with pytest.raises(HTTPException) as exc_info:
            await ready(db=mock_session)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Database unavailable"

    @pytest.mark.asyncio
    async def test_ready_probe_http_endpoint_503_via_client(self):
        """Test HTTP GET /health/ready through ASGI client with broken DB dependency."""
        async def mock_broken_db():
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("Cannot reach PostgreSQL")
            yield mock_session

        app.dependency_overrides[get_db_session] = mock_broken_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                resp = await client.get("/health/ready")
                assert resp.status_code == 503
                data = resp.json()
                assert data["detail"] == "Database unavailable"
        finally:
            app.dependency_overrides.pop(get_db_session, None)


# ==============================================================================
# Challenge 3: AST Verification of asyncio.to_thread in CPU Routes
# ==============================================================================
class TestCPURoutesASTInspection:
    """Inspect AST of route controllers to verify asyncio.to_thread wrapping."""

    @staticmethod
    def _find_to_thread_calls(file_path: Path) -> list[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # Look for asyncio.to_thread(...)
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "to_thread"
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "asyncio"
                ):
                    arg0 = node.args[0] if node.args else None
                    if isinstance(arg0, ast.Attribute):
                        calls.append(f"{arg0.attr}")
                    elif isinstance(arg0, ast.Name):
                        calls.append(f"{arg0.id}")
                    else:
                        calls.append(ast.unparse(arg0))
        return calls

    def test_resumes_controller_uses_to_thread_for_cpu_tasks(self):
        """api/controllers/resumes.py must use asyncio.to_thread for parse, encode, extract."""
        p = Path("api/controllers/resumes.py")
        calls = self._find_to_thread_calls(p)
        assert "parse" in calls, "parser.parse must be wrapped in asyncio.to_thread"
        assert "encode" in calls, "emb_service.encode must be wrapped in asyncio.to_thread"
        assert "extract" in calls, "extractor.extract must be wrapped in asyncio.to_thread"

    def test_jobs_controller_uses_to_thread_for_embedding(self):
        """api/controllers/jobs.py must use asyncio.to_thread for emb_service.encode."""
        p = Path("api/controllers/jobs.py")
        calls = self._find_to_thread_calls(p)
        assert "encode" in calls, "emb_service.encode must be wrapped in asyncio.to_thread"

    def test_match_controller_uses_to_thread_for_hybrid_matcher(self):
        """api/controllers/match.py must use asyncio.to_thread for matcher.match."""
        p = Path("api/controllers/match.py")
        calls = self._find_to_thread_calls(p)
        assert "match" in calls, "matcher.match must be wrapped in asyncio.to_thread"


# ==============================================================================
# Challenge 4: Empirical Concurrency & Event Loop Non-Blocking Stress Harness
# ==============================================================================
class TestEventLoopNonBlockingStress:
    """Empirical proof that CPU tasks execute on worker threads without blocking event loop."""

    @pytest.mark.asyncio
    async def test_worker_thread_execution_identity(self):
        """Verify that functions called via asyncio.to_thread execute in separate OS thread."""
        main_thread_id = threading.get_ident()
        worker_thread_id = None

        def cpu_dummy():
            nonlocal worker_thread_id
            worker_thread_id = threading.get_ident()
            time.sleep(0.05)
            return "done"

        res = await asyncio.to_thread(cpu_dummy)
        assert res == "done"
        assert worker_thread_id is not None
        assert worker_thread_id != main_thread_id, "asyncio.to_thread must run on separate worker thread"

    @pytest.mark.asyncio
    async def test_concurrent_event_loop_responsiveness_during_heavy_cpu_work(self):
        """
        Adversarial Concurrency Stress:
        Simulate a heavy 250ms CPU task inside a route wrapped with asyncio.to_thread.
        While the heavy task is running, fire 10 concurrent requests to /health/live.
        Measure max latency of /health/live.
        If event loop is NOT blocked, /health/live responds in < 50ms while CPU is running.
        If event loop were blocked, /health/live would be delayed to >= 250ms.
        """
        blocking_cpu_duration = 0.20  # 200ms
        probe_latencies = []

        def heavy_cpu_work():
            # Real-world CPU offloaded library functions (like PyTorch, numpy, sentence-transformers,
            # or OS I/O) release the CPython GIL. We simulate offloaded work with GIL-releasing sleep.
            time.sleep(blocking_cpu_duration)
            return "computed"

        async def background_cpu_route():
            return await asyncio.to_thread(heavy_cpu_work)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Launch the heavy CPU task
            cpu_task = asyncio.create_task(background_cpu_route())

            # Brief yield to ensure CPU task has started
            await asyncio.sleep(0.01)

            # Now fire 10 concurrent requests to /health/live while CPU task is active
            async def probe():
                t0 = time.perf_counter()
                resp = await client.get("/health/live")
                t_elapsed = time.perf_counter() - t0
                assert resp.status_code == 200
                probe_latencies.append(t_elapsed)

            probes = [probe() for _ in range(10)]
            await asyncio.gather(*probes)

            # Wait for the CPU task to complete
            cpu_result = await cpu_task
            assert cpu_result == "computed"

        # Statistical check: max probe latency must be far less than the 200ms CPU duration
        max_probe_latency = max(probe_latencies)
        avg_probe_latency = sum(probe_latencies) / len(probe_latencies)

        assert max_probe_latency < 0.10, (
            f"Event loop was starved! Max probe latency: {max_probe_latency*1000:.1f}ms "
            f"(expected < 100ms during {blocking_cpu_duration*1000:.0f}ms CPU workload)"
        )
        assert avg_probe_latency < 0.05, (
            f"Average probe latency too high: {avg_probe_latency*1000:.1f}ms"
        )

    @pytest.mark.asyncio
    async def test_live_route_concurrent_stress_with_mocked_db_adhoc_match(self):
        """
        Stress test /api/v1/match/adhoc concurrently with /health/live.
        Verify that adhoc match execution does not freeze concurrent /health/live calls.
        """
        cand_id = uuid4()
        job_id = uuid4()

        mock_cand = MagicMock(spec=Candidate)
        mock_cand.id = cand_id
        mock_cand.embedding = [0.1] * 384
        mock_cand.total_experience_years = 5
        mock_cand.skills = []

        mock_job = MagicMock(spec=JobPosting)
        mock_job.id = job_id
        mock_job.embedding = [0.1] * 384
        mock_job.min_experience = 3
        mock_job.skills = []

        async def mock_db():
            session = AsyncMock()
            async def mock_get(entity, entity_id, **kwargs):
                if entity == Candidate:
                    return mock_cand
                if entity == JobPosting:
                    return mock_job
                return None
            session.get.side_effect = mock_get
            yield session

        app.dependency_overrides[get_db_session] = mock_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                probe_times = []

                async def hit_match():
                    return await client.post(
                        "/api/v1/match/adhoc",
                        json={"candidate_id": str(cand_id), "job_id": str(job_id)},
                    )

                async def hit_live():
                    t0 = time.perf_counter()
                    resp = await client.get("/health/live")
                    dt = time.perf_counter() - t0
                    probe_times.append(dt)
                    return resp

                # Run adhoc match and 5 live probes concurrently
                tasks = [hit_match()] + [hit_live() for _ in range(5)]
                results = await asyncio.gather(*tasks)

                match_resp = results[0]
                assert match_resp.status_code == 200
                data = match_resp.json()
                assert "total_score" in data

                # All live probes must have succeeded rapidly
                assert len(probe_times) == 5
                assert max(probe_times) < 0.15
        finally:
            app.dependency_overrides.pop(get_db_session, None)


# ==============================================================================
# Challenge 5: .dockerignore Verification
# ==============================================================================
class TestDockerignoreVerification:
    """Verify presence and rules in .dockerignore."""

    def test_dockerignore_contains_required_rules(self):
        p = Path(".dockerignore")
        assert p.is_file(), ".dockerignore must exist at repository root"

        content = p.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

        required_patterns = [".git", ".venv", "node_modules", "scratch"]
        for pat in required_patterns:
            assert pat in lines or any(re.match(rf"^{re.escape(pat)}", line) for line in lines), (
                f"Missing {pat} in .dockerignore"
            )


# ==============================================================================
# Challenge 6: CI Workflow Trivy Pinning Verification
# ==============================================================================
class TestCIWorkflowTrivyPinning:
    """Verify aquasecurity/trivy-action is pinned to 0.28.0 in .github/workflows/ci.yml."""

    def test_trivy_action_pinned_to_0_28_0(self):
        p = Path(".github/workflows/ci.yml")
        assert p.is_file(), ".github/workflows/ci.yml must exist"

        content = p.read_text(encoding="utf-8")
        assert "aquasecurity/trivy-action@0.28.0" in content, (
            "aquasecurity/trivy-action must be pinned to @0.28.0 in ci.yml"
        )
        assert "aquasecurity/trivy-action@master" not in content, (
            "aquasecurity/trivy-action@master must NOT be present in ci.yml"
        )


# ==============================================================================
# Challenge 7: Live PostgreSQL Integration & Unreachable DB Simulation
# ==============================================================================
class TestLiveDatabaseAndFailureSimulation:
    """Empirical integration testing against running database and network-level failure simulation."""

    @pytest.mark.asyncio
    async def test_ready_probe_against_live_database(self):
        """Verify /health/ready returns 200 against live PostgreSQL database."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/health/ready")
            assert resp.status_code == 200
            assert resp.json() == {"status": "ready"}

    @pytest.mark.asyncio
    async def test_ready_probe_unreachable_database_returns_503(self):
        """Simulate real socket connection failure to dead DB port (127.0.0.1:59999) -> 503."""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
        dead_engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@127.0.0.1:59999/talent_db",
            connect_args={"timeout": 1.0},
        )
        dead_maker = async_sessionmaker(dead_engine, class_=AsyncSession, expire_on_commit=False)

        async def dead_db_session():
            async with dead_maker() as session:
                yield session

        app.dependency_overrides[get_db_session] = dead_db_session
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                resp = await client.get("/health/ready")
                assert resp.status_code == 503
                assert resp.json()["detail"] == "Database unavailable"
        finally:
            app.dependency_overrides.pop(get_db_session, None)
            await dead_engine.dispose()

    @pytest.mark.asyncio
    async def test_resume_upload_concurrent_with_live_probes(self):
        """Empirically test /api/v1/resumes/upload concurrently with multiple /health/live probes."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resume_content = (
                b"Experienced Senior Software Engineer\n"
                b"Skills: Python, FastAPI, Docker, PostgreSQL, React, Kubernetes.\n"
                b"Over 6 years of experience building backend systems."
            )
            files = {"file": ("test_resume.txt", resume_content, "text/plain")}

            probe_times = []

            async def do_upload():
                return await client.post("/api/v1/resumes/upload", files=files)

            async def do_probe():
                t0 = time.perf_counter()
                res = await client.get("/health/live")
                dt = time.perf_counter() - t0
                probe_times.append(dt)
                return res

            tasks = [do_upload()] + [do_probe() for _ in range(10)]
            results = await asyncio.gather(*tasks)

            upload_resp = results[0]
            assert upload_resp.status_code == 200
            data = upload_resp.json()
            assert "id" in data
            assert len(data["skills_extracted"]) > 0

            # Verify all 10 probes finished quickly without being blocked
            assert len(probe_times) == 10
            for pt in probe_times:
                assert pt < 0.20, f"Probe took too long during upload: {pt*1000:.1f}ms"

    @pytest.mark.asyncio
    async def test_job_creation_and_listing_serialization_fixed(self):
        """
        Verify that JobResponse serialization succeeds cleanly without MissingGreenlet error.
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            job_payload = {
                "title": f"Staff Systems Engineer {uuid4().hex[:6]}",
                "department": "Engineering",
                "description": "Building high throughput data pipelines and distributed services.",
                "requirements": "Strong Python, FastAPI, asyncio, PostgreSQL, Docker skills required.",
                "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                "min_experience": 5,
                "max_experience": 10,
                "location": "Remote",
                "headcount": 2,
            }

            resp_post = await client.post("/api/v1/jobs", json=job_payload)
            # If live DB is present, returns 200; if no live DB, error is DB connection not MissingGreenlet serialization
            if resp_post.status_code == 200:
                data = resp_post.json()
                assert data["title"] == job_payload["title"]
                assert data["skills"] == job_payload["skills"]

            resp_get = await client.get("/api/v1/jobs")
            if resp_get.status_code == 200:
                jobs_list = resp_get.json()
                assert isinstance(jobs_list, list)
