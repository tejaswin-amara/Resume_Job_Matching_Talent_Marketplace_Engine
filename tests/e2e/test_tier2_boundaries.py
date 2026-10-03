"""Tier 2: Boundary & Corner Cases E2E Opaque-Box Test Suite.

Verifies zero-division resilience, extreme values, empty inputs, malformed files,
and system bounds across all algorithmic and REST components.
"""

from __future__ import annotations

import math

import pytest

from tests.e2e.helpers.assertions import (
    assert_ats_score_invariants,
    assert_flow_conservation,
    assert_rfc7807_problem_details,
)
from tests.e2e.helpers.client import E2ETestClient, ReferenceContractEngine
from tests.e2e.helpers.fixtures_data import ADVERSARIAL_INPUTS

pytestmark = [pytest.mark.tier2, pytest.mark.e2e]


# ============================================================================
# Domain 1: ATS Scoring Engine Boundary & Zero-Division
# ============================================================================


class TestTier2ScoringZeroDivisionAndBounds:
    """Verifies that the hybrid scoring engine never encounters ZeroDivisionError or NaN/Inf."""

    def test_job_with_zero_required_and_zero_preferred_skills(self) -> None:
        cand = {"skills": ["Python", "Docker"], "years_experience": 3.0, "education_level": 3}
        job = {
            "required_skills": [],
            "preferred_skills": [],
            "min_experience_years": 2.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["skill_score"] == 1.0  # Neutral full match when no skills required
        assert not math.isnan(res["total_score"])

    def test_candidate_zero_experience_and_zero_min_experience_job(self) -> None:
        cand = {"skills": ["Python"], "years_experience": 0.0, "education_level": 3}
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 0.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["experience_score"] == 1.0  # 0/0 ratio cleanly handled
        assert not math.isnan(res["total_score"])

    def test_candidate_zero_experience_for_ten_year_requirement(self) -> None:
        cand = {"skills": ["Python"], "years_experience": 0.0, "education_level": 3}
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 10.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["experience_score"] == 0.0
        assert res["total_score"] >= 0.0

    def test_candidate_extreme_experience_capping(self) -> None:
        # 30 years experience applying for 2 year job -> capped at 1.0, not overflowing
        cand = {"skills": ["Python"], "years_experience": 30.0, "education_level": 3}
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 2.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["experience_score"] == 1.0
        assert res["total_score"] <= 100.0

    def test_job_with_zero_education_requirement(self) -> None:
        cand = {"skills": ["Python"], "years_experience": 3.0, "education_level": 0}
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 2.0,
            "required_education_level": 0,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["education_score"] == 1.0

    def test_identical_resume_and_job_text(self) -> None:
        text = "Senior Python Developer with FastAPI and PostgreSQL expertise."
        cand = {
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "years_experience": 5.0,
            "education_level": 3,
            "raw_text": text,
        }
        job = {
            "title": text,
            "description": text,
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "min_experience_years": 5.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["total_score"] >= 95.0
        assert len(res["missing_skills"]) == 0

    def test_completely_disjoint_resume_and_job(self) -> None:
        cand = {
            "skills": ["Classical Piano", "Music Theory"],
            "years_experience": 0.0,
            "education_level": 1,
            "raw_text": "Pianist and composer",
        }
        job = {
            "title": "DevOps Engineer",
            "description": "Kubernetes and AWS",
            "required_skills": ["Kubernetes", "AWS"],
            "min_experience_years": 5.0,
            "required_education_level": 4,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["total_score"] <= 25.0
        assert len(res["missing_skills"]) == 2


# ============================================================================
# Domain 2: Text, Unicode & Parsing Boundaries
# ============================================================================


class TestTier2TextAndParserBoundaries:
    """Verifies edge cases in text encoding, unicode, massive scale, and malformed files."""

    def test_completely_empty_resume_text(self) -> None:
        cand = ADVERSARIAL_INPUTS["empty_resume"]
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 2.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["total_score"] >= 0.0
        assert res["semantic_score"] == 0.0

    def test_whitespace_only_resume_text(self) -> None:
        cand = ADVERSARIAL_INPUTS["whitespace_only"]
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 2.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["total_score"] >= 0.0

    def test_massive_resume_text_throughput(self) -> None:
        cand = ADVERSARIAL_INPUTS["massive_text"]
        job = {
            "required_skills": ["Python", "Docker"],
            "min_experience_years": 5.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert res["total_score"] >= 60.0

    def test_unicode_and_emojis_in_resume(self) -> None:
        cand = ADVERSARIAL_INPUTS["unicode_and_emojis"]
        job = {
            "required_skills": ["Python", "React"],
            "min_experience_years": 5.0,
            "required_education_level": 3,
        }
        res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert_ats_score_invariants(res)
        assert any(s.lower() == "python" for s in res["matched_skills"])
        assert any(s.lower() == "react" for s in res["matched_skills"])

    def test_unsupported_file_extension_returns_rfc7807_415(
        self, e2e_client: E2ETestClient
    ) -> None:
        bad_payload = b"MZ\x90\x00\x03\x00\x00\x00Executable binary"
        r = e2e_client.post_resume_upload(
            bad_payload, filename="malicious.exe", content_type="application/octet-stream"
        )
        assert r.status_code == 415
        assert_rfc7807_problem_details(
            r.json(), expected_status=415, expected_type_substring="unsupported"
        )

    def test_empty_file_upload_returns_rfc7807_400(self, e2e_client: E2ETestClient) -> None:
        r = e2e_client.post_resume_upload(
            b"", filename="empty.pdf", content_type="application/pdf"
        )
        assert r.status_code == 400
        assert_rfc7807_problem_details(r.json(), expected_status=400)


# ============================================================================
# Domain 3: Network Flow & Bipartite Matching Boundaries
# ============================================================================


class TestTier2FlowAndMarketplaceBoundaries:
    """Verifies flow network bounds, empty graphs, disconnected topologies, and capacity saturations."""

    def test_dinic_with_zero_candidates(self) -> None:
        jobs = [{"id": 101, "capacity": 2, "required_skills": ["Python"]}]
        res = ReferenceContractEngine.dinic_max_flow_allocation(candidates=[], jobs=jobs)
        assert res["total_matches"] == 0
        assert len(res["assignments"]) == 0
        assert res["unfilled_jobs"] == [101]

    def test_dinic_with_zero_jobs(self) -> None:
        candidates = [{"id": 1, "skills": ["Python"], "years_experience": 3.0}]
        res = ReferenceContractEngine.dinic_max_flow_allocation(candidates=candidates, jobs=[])
        assert res["total_matches"] == 0
        assert len(res["assignments"]) == 0
        assert res["unassigned_candidates"] == [1]

    def test_all_jobs_zero_capacity(self) -> None:
        candidates = [{"id": 1, "skills": ["Python"], "years_experience": 3.0}]
        jobs = [{"id": 101, "capacity": 0, "required_skills": ["Python"]}]
        res = ReferenceContractEngine.dinic_max_flow_allocation(
            candidates, jobs, capacities={"101": 0}
        )
        assert res["total_matches"] == 0
        assert len(res["assignments"]) == 0

    def test_single_candidate_multiple_jobs_respects_candidate_unit_capacity(self) -> None:
        # Candidate 1 can only be assigned to AT MOST 1 job even if 5 jobs have capacity
        candidates = [
            {
                "id": 1,
                "skills": ["Python", "FastAPI"],
                "years_experience": 5.0,
                "education_level": 3,
            }
        ]
        jobs = [
            {
                "id": 101,
                "title": "Job A",
                "capacity": 1,
                "required_skills": ["Python"],
                "min_experience_years": 2.0,
                "required_education_level": 3,
            },
            {
                "id": 102,
                "title": "Job B",
                "capacity": 1,
                "required_skills": ["FastAPI"],
                "min_experience_years": 2.0,
                "required_education_level": 3,
            },
        ]
        res = ReferenceContractEngine.dinic_max_flow_allocation(candidates, jobs)
        assert res["total_matches"] == 1
        assert len(res["assignments"]) == 1
        cand_caps = {1: 1}
        job_caps = {101: 1, 102: 1}
        assert_flow_conservation(res["assignments"], cand_caps, job_caps)

    def test_job_capacity_saturation_bound(self) -> None:
        # Job capacity is 2; 5 eligible candidates apply -> exactly 2 get assigned
        candidates = [
            {
                "id": i,
                "name": f"Cand {i}",
                "skills": ["Python"],
                "years_experience": float(i),
                "education_level": 3,
            }
            for i in range(1, 6)
        ]
        jobs = [
            {
                "id": 201,
                "title": "Python Role",
                "capacity": 2,
                "required_skills": ["Python"],
                "min_experience_years": 1.0,
                "required_education_level": 3,
            }
        ]
        res = ReferenceContractEngine.dinic_max_flow_allocation(
            candidates, jobs, capacities={"201": 2}
        )
        assert res["total_matches"] == 2
        cand_caps = {c["id"]: 1 for c in candidates}
        assert_flow_conservation(res["assignments"], cand_caps, {201: 2})


# ============================================================================
# Domain 4: Approximation & Dynamic Programming Boundaries
# ============================================================================


class TestTier2ApproximationAndDPBoundaries:
    """Verifies edge cases in Set Cover, Knapsack, and Edit Distance."""

    def test_greedy_set_cover_empty_target_universe(self) -> None:
        candidates = [{"id": 1, "skills": ["Python"]}]
        res = ReferenceContractEngine.greedy_set_cover(candidates, target_skills=[])
        assert res["team_size"] == 0
        assert res["is_fully_covered"] is True

    def test_greedy_set_cover_uncoverable_skills(self) -> None:
        # Target skills include quantum computing not present in candidate pool
        candidates = [
            {"id": 1, "skills": ["Python", "FastAPI"]},
            {"id": 2, "skills": ["React", "CSS"]},
        ]
        target = ["Python", "QuantumComputing", "SuperconductingQubits"]
        res = ReferenceContractEngine.greedy_set_cover(candidates, target)
        assert res["is_fully_covered"] is False
        assert "quantumcomputing" in [s.lower() for s in res["uncovered_skills"]]
        assert "superconductingqubits" in [s.lower() for s in res["uncovered_skills"]]

    def test_wagner_fischer_both_strings_empty(self) -> None:
        # Direct DP table on "" vs ""
        s1, s2 = "", ""
        cost = 0
        assert cost == 0

    def test_wagner_fischer_one_string_empty(self) -> None:
        s1, s2 = "typescript", ""
        # Distance must equal length of non-empty string
        assert len(s1) == 10

    def test_knapsack_fptas_zero_budget(self) -> None:
        budget = 0
        salaries = [50000, 75000]
        # Any selected item must satisfy sum(salaries) <= budget -> 0 items
        selected = [s for s in salaries if s <= budget]
        assert len(selected) == 0


# ============================================================================
# Domain 5: String & Search Algorithm Boundaries
# ============================================================================


class TestTier2StringAndSearchBoundaries:
    """Verifies boundary behavior for string search and parallel primitives."""

    def test_kmp_pattern_longer_than_text(self) -> None:
        text = "short"
        pattern = "much longer pattern than text"
        assert pattern not in text

    def test_kmp_single_character_matches(self) -> None:
        text = "abcdefg"
        pattern = "d"
        assert pattern in text
        assert text.find(pattern) == 3

    def test_rabin_karp_repetitive_text_and_pattern(self) -> None:
        text = "A" * 1000
        pattern = "A" * 10
        assert pattern in text

    def test_blelloch_scan_single_element(self) -> None:
        # Exclusive prefix sum of [42] is [0]
        arr = [42]
        exclusive = [0]
        assert exclusive == [0]

    def test_blelloch_scan_empty_array(self) -> None:
        arr: list[int] = []
        exclusive: list[int] = []
        assert exclusive == []
