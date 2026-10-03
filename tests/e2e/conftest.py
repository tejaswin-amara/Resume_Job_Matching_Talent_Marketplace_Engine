"""Pytest fixtures and configuration for the E2E Opaque-Box Test Suite."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e.helpers.client import E2ETestClient
from tests.e2e.helpers.fixtures_data import (
    ADVERSARIAL_INPUTS,
    CANDIDATES_FIXTURES,
    DOCX_MAGIC_BYTES,
    JOB_REQUISITIONS_FIXTURES,
    PDF_MAGIC_BYTES,
    SAMPLE_SKILLS_TAXONOMY,
    TXT_SAMPLE_BYTES,
)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for 4-tier E2E testing."""
    config.addinivalue_line(
        "markers", "tier1: Tier 1 Feature Coverage tests (>=5 tests per feature)"
    )
    config.addinivalue_line(
        "markers", "tier2: Tier 2 Boundary & Corner Cases (zero-division, extreme values)"
    )
    config.addinivalue_line(
        "markers", "tier3: Tier 3 Cross-Feature Combinations (pairwise interactions)"
    )
    config.addinivalue_line(
        "markers", "tier4: Tier 4 Real-World Application Scenarios (end-to-end user workflows)"
    )
    config.addinivalue_line("markers", "e2e: End-to-end opaque-box tests")


@pytest.fixture(scope="session")
def e2e_client() -> E2ETestClient:
    """Provides a unified client for REST API endpoints and contract validation."""
    return E2ETestClient()


@pytest.fixture
def candidates() -> list[dict[str, Any]]:
    """Golden candidate dataset."""
    return [dict(c) for c in CANDIDATES_FIXTURES]


@pytest.fixture
def jobs() -> list[dict[str, Any]]:
    """Golden job requisitions dataset."""
    return [dict(j) for j in JOB_REQUISITIONS_FIXTURES]


@pytest.fixture
def adversarial_data() -> dict[str, Any]:
    """Adversarial and boundary test inputs."""
    return ADVERSARIAL_INPUTS


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    return PDF_MAGIC_BYTES


@pytest.fixture
def sample_docx_bytes() -> bytes:
    return DOCX_MAGIC_BYTES


@pytest.fixture
def sample_txt_bytes() -> bytes:
    return TXT_SAMPLE_BYTES


@pytest.fixture
def skills_taxonomy() -> list[str]:
    return list(SAMPLE_SKILLS_TAXONOMY)
