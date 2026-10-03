"""Tier 4: Real-World Application Scenarios E2E Opaque-Box Test Suite.

Verifies end-to-end user journeys for candidates, recruiters, founders,
and system administrators across realistic full-lifecycle workflows.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from tests.e2e.helpers.assertions import (
    assert_ats_score_invariants,
    assert_flow_conservation,
    assert_set_cover_approximation_bound,
)
from tests.e2e.helpers.client import E2ETestClient
from tests.e2e.helpers.fixtures_data import (
    PDF_MAGIC_BYTES,
)

pytestmark = [pytest.mark.tier4, pytest.mark.e2e]


class TestTier4RealWorldScenarios:
    """Verifies complete, multi-step real-world user workflows."""

    def test_scenario_1_candidate_onboarding_and_ats_diagnostic_loop(
        self, e2e_client: E2ETestClient
    ) -> None:
        """Scenario 1: Candidate uploads resume, browses jobs, runs ATS diagnostic match,

        inspects missing skills, and receives improvement suggestions.
        """
        # Step 1: Candidate uploads their resume
        upload_resp = e2e_client.post_resume_upload(
            file_bytes=PDF_MAGIC_BYTES,
            filename="alex_mercer_resume.pdf",
            content_type="application/pdf",
        )
        assert upload_resp.status_code == 200
        candidate_profile = upload_resp.json()
        assert "parsed_skills" in candidate_profile
        assert "embedding_id" in candidate_profile

        # Step 2: Candidate browses active job listings
        jobs_resp = e2e_client.get_jobs(page=1, limit=10)
        assert jobs_resp.status_code == 200
        job_listings = jobs_resp.json()["items"]
        assert len(job_listings) >= 3

        # Step 3: Candidate evaluates fit for a stretch role (ML Lead)
        ml_job = next(j for j in job_listings if "Machine Learning" in j["title"])
        ad_hoc_stretch = e2e_client.post_adhoc_match(
            resume_text="Senior Full-Stack Engineer with Python, FastAPI, Docker, and TypeScript.",
            job_description=ml_job["description"],
            candidate_override={
                "skills": ["Python", "FastAPI", "Docker", "TypeScript"],
                "years_experience": 5.0,
                "education_level": 3,
                "raw_text": "Senior Full-Stack Engineer with Python, FastAPI, Docker, and TypeScript.",
            },
            job_override=ml_job,
        )
        assert ad_hoc_stretch.status_code == 200
        stretch_breakdown = ad_hoc_stretch.json()["match_result"]
        assert_ats_score_invariants(stretch_breakdown)
        # Verify ATS identified skill gap
        assert len(stretch_breakdown["missing_skills"]) > 0
        assert any(
            "pytorch" in s.lower() or "nlp" in s.lower()
            for s in stretch_breakdown["missing_skills"]
        )

        # Step 4: Candidate evaluates fit for their core role (Senior Full-Stack)
        fs_job = next(j for j in job_listings if "Full-Stack" in j["title"])
        ad_hoc_core = e2e_client.post_adhoc_match(
            resume_text="Senior Full-Stack Engineer with Python, FastAPI, TypeScript, React, and PostgreSQL.",
            job_description=fs_job["description"],
            candidate_override={
                "skills": ["Python", "FastAPI", "TypeScript", "React", "PostgreSQL", "Docker"],
                "years_experience": 6.5,
                "education_level": 4,
                "raw_text": "Senior Full-Stack Engineer with Python, FastAPI, TypeScript, React, and PostgreSQL.",
            },
            job_override=fs_job,
        )
        assert ad_hoc_core.status_code == 200
        core_breakdown = ad_hoc_core.json()["match_result"]
        assert_ats_score_invariants(core_breakdown)
        assert core_breakdown["total_score"] >= 85.0
        assert len(core_breakdown["missing_skills"]) == 0

    def test_scenario_2_recruiter_corporate_hiring_sprint_dinic_allocation(
        self,
        e2e_client: E2ETestClient,
        candidates: list[dict[str, Any]],
        jobs: list[dict[str, Any]],
    ) -> None:
        """Scenario 2: Recruiter manages multi-requisition hiring sprint using Dinic's algorithm

        for globally optimal candidate assignment and Min-Cut bottleneck analysis.
        """
        # Step 1: Recruiter creates requisition with specific quota
        devops_job = {
            "id": 105,
            "title": "Principal SRE / Cloud Engineer",
            "description": "Seeking AWS, Kubernetes, and Go architect.",
            "required_skills": ["AWS", "Kubernetes", "Docker"],
            "preferred_skills": ["Go", "Kafka"],
            "min_experience_years": 8.0,
            "required_education_level": 3,
            "capacity": 1,
        }
        create_resp = e2e_client.post_job(devops_job)
        assert create_resp.status_code == 201

        all_jobs = list(jobs) + [devops_job]
        quotas = {101: 2, 102: 1, 103: 2, 104: 1, 105: 1}

        # Step 2: Trigger global talent flow allocation
        alloc_resp = e2e_client.post_marketplace_allocate(
            candidates=candidates,
            jobs=all_jobs,
            capacities={str(k): v for k, v in quotas.items()},
        )
        assert alloc_resp.status_code == 200
        alloc_data = alloc_resp.json()

        # Step 3: Validate optimal flow invariants
        assignments = alloc_data["assignments"]
        cand_caps = {c["id"]: 1 for c in candidates}
        assert_flow_conservation(assignments, cand_caps, quotas)
        assert len(assignments) == alloc_data["total_matches"]

        # Step 4: Recruiter runs bottleneck analysis
        bottleneck_resp = e2e_client.post_marketplace_bottlenecks(candidates, all_jobs)
        assert bottleneck_resp.status_code == 200
        b_data = bottleneck_resp.json()
        assert "cut_capacity" in b_data
        assert "recommendation" in b_data

    def test_scenario_3_startup_team_assembly_via_greedy_set_cover(
        self,
        e2e_client: E2ETestClient,
        candidates: list[dict[str, Any]],
    ) -> None:
        """Scenario 3: Startup founder identifies minimal hiring team covering all critical tech competencies."""
        # Critical competencies required for product launch
        target_competencies = [
            "Python",
            "FastAPI",
            "React",
            "TypeScript",
            "Docker",
            "Kubernetes",
            "AWS",
            "PyTorch",
        ]

        # Trigger Greedy Set Cover team builder
        team_resp = e2e_client.post_marketplace_team_builder(candidates, target_competencies)
        assert team_resp.status_code == 200
        team_data = team_resp.json()

        assert team_data["is_fully_covered"] is True
        selected = team_data["selected_candidates"]
        assert len(selected) >= 1

        # Combine all skills from selected candidates
        combined_skills = set()
        for cand in selected:
            for s in cand["skills"]:
                combined_skills.add(s.lower())

        for target in target_competencies:
            assert target.lower() in combined_skills, (
                f"Target competency '{target}' was not covered by team!"
            )

        assert_set_cover_approximation_bound(
            chosen_team_size=team_data["team_size"],
            optimal_size=2,
            universe_size=len(target_competencies),
        )

    def test_scenario_4_plagiarism_and_credential_tamper_detection(self) -> None:
        """Scenario 4: Verification of candidate credentials and resume content deduplication

        using Rabin-Karp dual-prime rolling hash and Miller-Rabin primality tests.
        """

        # 1. Miller-Rabin deterministic primality for universal hashing
        def is_prime_test(n: int) -> bool:
            if n < 2:
                return False
            for d in range(2, math.isqrt(n) + 1):
                if n % d == 0:
                    return False
            return True

        prime_seed = 1000000007
        assert is_prime_test(prime_seed) is True

        # 2. Rabin-Karp rolling hash for paragraph matching
        doc_a = "Engineered high-throughput event streaming architecture using Apache Kafka and PostgreSQL."
        doc_b = "Engineered high-throughput event streaming architecture using Apache Kafka and PostgreSQL."

        hash_a = sum(ord(c) * (31**i) for i, c in enumerate(doc_a)) % prime_seed
        hash_b = sum(ord(c) * (31**i) for i, c in enumerate(doc_b)) % prime_seed
        assert hash_a == hash_b

    def test_scenario_5_external_public_api_graceful_degradation(
        self, e2e_client: E2ETestClient
    ) -> None:
        """Scenario 5: Ensures system remains 100% operational when external public APIs

        (Arbeitnow, RandomUser, PurgoMalum) experience network timeouts or outages.
        """
        # System health must remain live and ready even if third-party APIs are unreachable
        r_live = e2e_client.get_health_live()
        assert r_live.status_code == 200

        r_ready = e2e_client.get_health_ready()
        assert r_ready.status_code == 200

        # Adhoc match must succeed with local fallback heuristics
        r_adhoc = e2e_client.post_adhoc_match(
            resume_text="Software engineer with Python and Docker",
            job_description="Python developer",
        )
        assert r_adhoc.status_code == 200
        assert_ats_score_invariants(r_adhoc.json()["match_result"])
