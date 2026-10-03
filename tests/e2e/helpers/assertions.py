"""Domain-specific assertions for E2E opaque-box testing.

Ensures mathematical correctness, RFC 7807 compliance, zero-library constraints,
and network flow conservation laws without tying tests to internal implementation details.
"""

from __future__ import annotations

import ast
import math
from typing import Any


def assert_ats_score_invariants(
    score_data: dict[str, Any],
    candidate_skills: list[str] | None = None,
    job_required_skills: list[str] | None = None,
    job_preferred_skills: list[str] | None = None,
    tolerance: float = 1e-4,
) -> None:
    """Verifies that an ATS scoring response satisfies all mathematical and domain invariants.

    Formula contract from PROJECT.md:
        total = 100 * (0.40 * semantic + 0.35 * skill + 0.15 * experience + 0.10 * education)
    """
    assert isinstance(score_data, dict), f"Expected dict for score_data, got {type(score_data)}"

    # Required keys in breakdown
    required_keys = [
        "total_score",
        "semantic_score",
        "skill_score",
        "experience_score",
        "education_score",
    ]
    for k in required_keys:
        assert k in score_data, f"Missing required scoring signal: '{k}' in {score_data}"
        val = score_data[k]
        assert isinstance(val, (int, float)), (
            f"Expected numeric score for '{k}', got {type(val)}: {val}"
        )
        assert not math.isnan(val), f"Score for '{k}' must not be NaN"
        assert not math.isinf(val), f"Score for '{k}' must not be Inf"

    total = float(score_data["total_score"])
    sem = float(score_data["semantic_score"])
    skill = float(score_data["skill_score"])
    exp = float(score_data["experience_score"])
    edu = float(score_data["education_score"])

    # Component scores must be normalized between 0.0 and 1.0
    for name, val in [
        ("semantic", sem),
        ("skill", skill),
        ("experience", exp),
        ("education", edu),
    ]:
        assert 0.0 - tolerance <= val <= 1.0 + tolerance, (
            f"Component score '{name}' = {val} out of bounds [0.0, 1.0]"
        )

    # Total score must be between 0.0 and 100.0
    assert 0.0 - tolerance <= total <= 100.0 + tolerance, (
        f"Total score = {total} out of bounds [0.0, 100.0]"
    )

    # Exact weighted formula verification
    expected_total = 100.0 * (0.40 * sem + 0.35 * skill + 0.15 * exp + 0.10 * edu)
    assert (
        abs(total - expected_total) <= tolerance or abs(total - round(expected_total, 2)) <= 0.02
    ), (
        f"ATS formula mismatch: actual total={total}, calculated expected={expected_total} "
        f"(sem={sem}, skill={skill}, exp={exp}, edu={edu})"
    )

    # Verify explainability structures if present
    if "matched_skills" in score_data:
        matched = score_data["matched_skills"]
        assert isinstance(matched, list), f"matched_skills must be a list, got {type(matched)}"
        if candidate_skills is not None:
            cand_lower = {s.lower() for s in candidate_skills}
            for m in matched:
                assert m.lower() in cand_lower or any(m.lower() in c for c in cand_lower), (
                    f"Matched skill '{m}' not in candidate skills {candidate_skills}"
                )

    if "missing_skills" in score_data:
        missing = score_data["missing_skills"]
        assert isinstance(missing, list), f"missing_skills must be a list, got {type(missing)}"

    if "improvement_suggestions" in score_data:
        suggestions = score_data["improvement_suggestions"]
        assert isinstance(suggestions, list), (
            f"improvement_suggestions must be a list, got {type(suggestions)}"
        )


def assert_rfc7807_problem_details(
    payload: dict[str, Any],
    expected_status: int,
    expected_type_substring: str | None = None,
) -> None:
    """Verifies that an error response strictly complies with RFC 7807 Problem Details specification."""
    assert isinstance(payload, dict), f"RFC 7807 response must be JSON object, got {type(payload)}"

    for required_field in ["type", "title", "status", "detail"]:
        assert required_field in payload, (
            f"RFC 7807 violation: missing required field '{required_field}' in payload: {payload}"
        )

    assert payload["status"] == expected_status, (
        f"Status code mismatch in RFC 7807 payload: expected {expected_status}, got {payload['status']}"
    )

    assert isinstance(payload["title"], str) and len(payload["title"]) > 0, (
        f"RFC 7807 'title' must be non-empty string: {payload.get('title')}"
    )
    assert isinstance(payload["detail"], str) and len(payload["detail"]) > 0, (
        f"RFC 7807 'detail' must be non-empty string: {payload.get('detail')}"
    )

    if expected_type_substring:
        assert expected_type_substring.lower() in str(payload["type"]).lower(), (
            f"Expected '{expected_type_substring}' in RFC 7807 'type', got '{payload['type']}'"
        )


def assert_flow_conservation(
    assignments: list[dict[str, Any]],
    candidate_capacities: dict[int, int],
    job_capacities: dict[int, int],
    total_flow: int | None = None,
) -> None:
    """Verifies network flow conservation and capacity constraints for talent marketplace allocation."""
    assert isinstance(assignments, list), f"Assignments must be a list, got {type(assignments)}"

    cand_usage: dict[int, int] = {}
    job_usage: dict[int, int] = {}

    for assign in assignments:
        cid = assign.get("candidate_id")
        jid = assign.get("job_id")
        assert cid is not None, f"Assignment missing candidate_id: {assign}"
        assert jid is not None, f"Assignment missing job_id: {assign}"

        cand_usage[cid] = cand_usage.get(cid, 0) + 1
        job_usage[jid] = job_usage.get(jid, 0) + 1

    # Candidate capacity constraints
    for cid, usage in cand_usage.items():
        cap = candidate_capacities.get(cid, 1)
        assert usage <= cap, (
            f"Flow violation: Candidate {cid} assigned {usage} times, exceeding capacity {cap}"
        )

    # Job capacity constraints
    for jid, usage in job_usage.items():
        cap = job_capacities.get(jid, 1)
        assert usage <= cap, (
            f"Flow violation: Job {jid} assigned {usage} times, exceeding capacity {cap}"
        )

    if total_flow is not None:
        assert len(assignments) == total_flow, (
            f"Total flow count mismatch: expected {total_flow}, actual assignments={len(assignments)}"
        )


def assert_zero_library_compliance(source_code: str, file_path: str = "<unknown>") -> None:
    """Verifies that Python source code contains ZERO forbidden imports per DSA-3 Core Cardinal Constraint."""
    forbidden_modules = {
        "collections",
        "heapq",
        "bisect",
        "networkx",
        "scipy",
        "numpy",
        "queue",
        "array",
        "pandas",
    }

    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error while parsing {file_path}: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_pkg = alias.name.split(".")[0]
                assert base_pkg not in forbidden_modules, (
                    f"CARDINAL CONSTRAINT VIOLATION in {file_path}:{node.lineno}: "
                    f"Forbidden import '{alias.name}' detected!"
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_pkg = node.module.split(".")[0]
                assert base_pkg not in forbidden_modules, (
                    f"CARDINAL CONSTRAINT VIOLATION in {file_path}:{node.lineno}: "
                    f"Forbidden import from '{node.module}' detected!"
                )


def assert_set_cover_approximation_bound(
    chosen_team_size: int,
    optimal_size: int,
    universe_size: int,
) -> None:
    """Verifies that the Greedy Set Cover output satisfies the theoretical (1 + ln n) approximation bound."""
    if universe_size <= 1:
        bound = 1.0
    else:
        bound = 1.0 + math.log(universe_size)

    max_allowed = math.ceil(optimal_size * bound)
    assert chosen_team_size <= max_allowed, (
        f"Greedy Set Cover approximation bound violated: chosen size {chosen_team_size} > "
        f"allowed bound {max_allowed} (optimal={optimal_size}, universe={universe_size}, ratio={chosen_team_size / optimal_size:.2f})"
    )
