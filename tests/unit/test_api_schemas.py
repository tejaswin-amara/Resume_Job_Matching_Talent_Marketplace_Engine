import uuid

import pytest
from pydantic import ValidationError

from api.schemas import JobCreate, MatchResultResponse


def test_job_creation_schema_validates():
    job = JobCreate(title="Engineer", description="Desc", requirements="Req")
    assert job.title == "Engineer"


def test_job_creation_schema_rejects_missing_title():
    with pytest.raises(ValidationError):
        JobCreate(description="Desc", requirements="Req")


def test_match_result_schema_serializes_correctly():
    uid = uuid.uuid4()
    res = MatchResultResponse(
        candidate_id=uid,
        job_id=uid,
        total_score=80.0,
        semantic_score=80.0,
        skill_score=80.0,
        experience_score=80.0,
        education_score=80.0,
        matched_skills=[],
        missing_skills=[],
        suggestions=[],
    )
    assert res.candidate_id == uid
    assert res.total_score == 80.0
