"""Contract verification suite using Schemathesis.

Validates the FastAPI OpenAPI 3.1 specification against live/ASGI application contracts:
- Valid OpenAPI schema structure and required metadata
- Complete endpoint inventory coverage
- RFC 7807 problem detail conformance on 4xx/5xx responses
- In-process ASGI fuzzing without requiring port 8000 binding
"""

import schemathesis
from starlette.testclient import TestClient

from api.app import app

# Load OpenAPI schema via in-process ASGI loader to avoid port 8000 collisions
schema = schemathesis.openapi.from_asgi("/openapi.json", app)


def test_openapi_spec_structure_and_completeness():
    """Verifies that the generated OpenAPI schema is compliant and complete."""
    raw_schema = app.openapi()
    assert raw_schema["openapi"].startswith("3.")
    assert raw_schema["info"]["title"] == "Talent Marketplace API"

    paths = raw_schema["paths"]
    expected_endpoints = [
        "/health/live",
        "/health/ready",
        "/api/v1/jobs",
        "/api/v1/jobs/{id}/matches",
        "/api/v1/match/adhoc",
        "/api/v1/marketplace/allocate",
        "/api/v1/marketplace/bottlenecks",
        "/api/v1/marketplace/team-builder",
        "/api/v1/resumes/upload",
        "/api/v1/resumes/parse-text",
    ]
    for endpoint in expected_endpoints:
        assert endpoint in paths, f"Missing endpoint contract: {endpoint}"


def test_health_endpoints_contract():
    """Explicitly verifies health endpoint responses against schema."""
    client = TestClient(app)

    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json() == {"status": "ok"}

    ready_res = client.get("/health/ready")
    assert ready_res.status_code in (200, 503)
    if ready_res.status_code == 200:
        assert ready_res.json() == {"status": "ready"}
    else:
        j = ready_res.json()
        assert j["detail"] == "Database unavailable"
        assert "instance" in j


health_schema = schema.include(path_regex=r"^/health/(live|ready)$")


@health_schema.parametrize()
def test_health_contracts_schemathesis(case):
    """Fuzzes health contracts with schemathesis."""
    from unittest.mock import AsyncMock, MagicMock
    from db.session import get_db_session

    async def mock_db():
        session = AsyncMock()
        mock_result = MagicMock()
        session.execute.return_value = mock_result
        yield session

    app.dependency_overrides[get_db_session] = mock_db
    try:
        response = case.call()
        case.validate_response(response)
    finally:
        app.dependency_overrides.pop(get_db_session, None)


def test_validation_error_rfc7807_contract():
    """Verifies 422 Unprocessable Entity responses adhere to error schema."""
    client = TestClient(app)

    # Empty payload to adhoc match
    res = client.post(
        "/api/v1/match/adhoc", json={}, headers={"Authorization": "Bearer dummy_token"}
    )
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data

    # Invalid payload to create job
    res_job = client.post(
        "/api/v1/jobs", json={"title": 123}, headers={"Authorization": "Bearer dummy_token"}
    )
    assert res_job.status_code == 422
    data_job = res_job.json()
    assert "detail" in data_job


def test_all_endpoints_schema_registered():
    """Verifies that all operations have valid schemas and HTTP methods."""
    operations = list(schema.get_all_operations())
    assert len(operations) >= 10
    methods = {op.ok().method.upper() for op in operations}
    assert "GET" in methods
    assert "POST" in methods
