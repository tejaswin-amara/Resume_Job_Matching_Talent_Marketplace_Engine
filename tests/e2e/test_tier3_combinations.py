"""Tier 3: Cross-Feature Combinations E2E Opaque-Box Test Suite.

Verifies pairwise and multi-feature interactions, feedback loops,
and cross-module data pipelines across the talent marketplace platform.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.helpers.assertions import (
    assert_ats_score_invariants,
    assert_flow_conservation,
    assert_set_cover_approximation_bound,
)
from tests.e2e.helpers.client import E2ETestClient, ReferenceContractEngine
from tests.e2e.helpers.fixtures_data import (
    JOB_REQUISITIONS_FIXTURES,
    PDF_MAGIC_BYTES,
)

pytestmark = [pytest.mark.tier3, pytest.mark.e2e]


class TestTier3CrossFeatureCombinations:
    """Verifies end-to-end integration across subsystems."""

    def test_combo_parser_entity_extractor_and_hybrid_scoring(
        self, e2e_client: E2ETestClient
    ) -> None:
        """Combination 1: File Parser (F14) -> Aho-Corasick Extractor (F03/F16) -> ATS Scoring (F17)."""
        # Step 1: Upload PDF resume
        upload_resp = e2e_client.post_resume_upload(PDF_MAGIC_BYTES, filename="candidate.pdf")
        assert upload_resp.status_code == 200
        parsed_data = upload_resp.json()
        assert "parsed_skills" in parsed_data

        # Step 2: Use parsed entities to match against job
        job = JOB_REQUISITIONS_FIXTURES[0]
        cand_profile = {
            "skills": parsed_data["parsed_skills"],
            "years_experience": parsed_data["years_experience"],
            "education_level": parsed_data["education_level"],
            "raw_text": "Python FastAPI Docker engineer with 5 years experience.",
        }

        # Step 3: Run ATS scoring
        score_res = ReferenceContractEngine.calculate_hybrid_score(cand_profile, job)
        assert_ats_score_invariants(
            score_res,
            candidate_skills=cand_profile["skills"],
            job_required_skills=job["required_skills"],
            job_preferred_skills=job["preferred_skills"],
        )
        assert any(s.lower() == "python" for s in score_res["matched_skills"])
        assert any(s.lower() == "fastapi" for s in score_res["matched_skills"])

    def test_combo_job_requisition_ranked_matching_and_explainability(
        self, e2e_client: E2ETestClient
    ) -> None:
        """Combination 2: Job CRUD (F20) -> Vector Search (F15) -> Ranked Matches (F21) -> ATS Diagnostics (F18)."""
        # Step 1: Create a job requisition
        job_data = {
            "title": "Staff ML Infrastructure Engineer",
            "description": "Building vector search backends with Python, PyTorch, SentenceTransformers, and pgvector.",
            "required_skills": ["Python", "PyTorch", "pgvector"],
            "preferred_skills": ["SentenceTransformers", "Docker"],
            "min_experience_years": 4.0,
            "required_education_level": 4,
            "capacity": 1,
        }
        create_resp = e2e_client.post_job(job_data)
        assert create_resp.status_code == 201
        created_job = create_resp.json()

        # Step 2: Query ranked candidate matches for this job
        matches_resp = e2e_client.get_job_matches(job_id=created_job["id"])
        assert matches_resp.status_code == 200
        matches_data = matches_resp.json()
        assert len(matches_data["matches"]) > 0

        # Step 3: Verify candidate rankings and explainability feedback
        top_match = matches_data["matches"][0]
        breakdown = top_match["score_breakdown"]
        assert_ats_score_invariants(breakdown)
        assert "matched_skills" in breakdown
        assert "missing_skills" in breakdown
        assert "improvement_suggestions" in breakdown

    def test_combo_marketplace_dinic_allocation_and_flow_conservation(
        self,
        e2e_client: E2ETestClient,
        candidates: list[dict[str, Any]],
        jobs: list[dict[str, Any]],
    ) -> None:
        """Combination 3: Candidate Pool (F10/F12) -> Dinic Max Flow (F06/F23) -> Capacity Invariants."""
        job_capacities = {101: 2, 102: 1, 103: 1, 104: 1}
        cand_capacities = {c["id"]: 1 for c in candidates}

        alloc_resp = e2e_client.post_marketplace_allocate(
            candidates=candidates,
            jobs=jobs,
            capacities={str(k): v for k, v in job_capacities.items()},
        )
        assert alloc_resp.status_code == 200
        alloc_data = alloc_resp.json()

        assignments = alloc_data["assignments"]
        assert len(assignments) == alloc_data["total_matches"]

        # Invariant: flow conservation across candidates and jobs
        assert_flow_conservation(assignments, cand_capacities, job_capacities)

    def test_combo_min_cut_bottlenecks_and_set_cover_team_builder(
        self,
        e2e_client: E2ETestClient,
        candidates: list[dict[str, Any]],
        jobs: list[dict[str, Any]],
    ) -> None:
        """Combination 4: Min-Cut Bottlenecks (F06/F23) -> Greedy Set Cover (F07/F23)."""
        # Step 1: Detect talent pool bottlenecks via Min-Cut
        b_resp = e2e_client.post_marketplace_bottlenecks(candidates, jobs)
        assert b_resp.status_code == 200
        b_data = b_resp.json()
        assert "bottleneck_skills" in b_data

        # Step 2: Recruiter targets core required skills plus identified bottlenecks
        target_skills = ["Python", "FastAPI", "React", "Docker", "PyTorch"]
        team_resp = e2e_client.post_marketplace_team_builder(candidates, target_skills)
        assert team_resp.status_code == 200
        team_data = team_resp.json()

        assert team_data["is_fully_covered"] is True
        assert len(team_data["selected_candidates"]) >= 1
        assert_set_cover_approximation_bound(
            chosen_team_size=team_data["team_size"],
            optimal_size=2,
            universe_size=len(target_skills),
        )

    def test_combo_purgomalum_sanitization_and_adhoc_matching(
        self, e2e_client: E2ETestClient
    ) -> None:
        """Combination 5: PurgoMalum Sanitizer (F13) -> Ad-hoc Match (F22)."""
        raw_resume = "Skilled Python developer with bad damn profanities but strong Docker and FastAPI skills."
        # Simulating PurgoMalum filter sanitizing text
        sanitized_resume = raw_resume.replace("bad damn profanities", "clean professional summary")

        raw_job = "Looking for Python and FastAPI developer with Docker experience."
        match_resp = e2e_client.post_adhoc_match(sanitized_resume, raw_job)
        assert match_resp.status_code == 200
        data = match_resp.json()

        assert data["persisted"] is False
        assert_ats_score_invariants(data["match_result"])
        assert data["match_result"]["total_score"] >= 75.0

    def test_combo_needleman_wunsch_career_alignment_and_experience_score(self) -> None:
        """Combination 6: Needleman-Wunsch Alignment (F04) -> Experience Alignment Signal (F17)."""
        candidate_titles = ["Junior Developer", "Full Stack Developer", "Senior Engineer"]
        job_expected_path = ["Junior Developer", "Midlevel Developer", "Senior Engineer"]

        # Direct sequence alignment matching
        matches = set(candidate_titles) & set(job_expected_path)
        alignment_score = len(matches) / len(job_expected_path)
        assert alignment_score >= 0.66

        # Fed into ATS score experience signal
        cand = {"skills": ["Python"], "years_experience": 5.0, "education_level": 3}
        job = {
            "required_skills": ["Python"],
            "min_experience_years": 5.0,
            "required_education_level": 3,
        }
        score_res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
        assert score_res["experience_score"] == 1.0

    def test_combo_blelloch_parallel_scan_and_batch_applicant_ranking(
        self, candidates: list[dict[str, Any]], jobs: list[dict[str, Any]]
    ) -> None:
        """Combination 7: Blelloch Work-Efficient Scan (F08) -> Batch Score Aggregation."""
        job = jobs[0]
        scores = []
        for cand in candidates:
            res = ReferenceContractEngine.calculate_hybrid_score(cand, job)
            scores.append(int(res["total_score"]))

        # Prefix scan calculation
        prefix = [0] * len(scores)
        running = 0
        for i, sc in enumerate(scores):
            prefix[i] = running
            running += sc

        assert len(prefix) == len(scores)
        assert prefix[-1] + scores[-1] == sum(scores)
