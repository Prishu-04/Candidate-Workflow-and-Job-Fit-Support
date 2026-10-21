from datetime import date

import pytest
from pydantic import ValidationError

from app.data.schemas import (
    AssessmentRecord,
    CandidateProfile,
    ChunkMetadata,
    DocumentSource,
    EvaluationCase,
    JobDescription,
)


def make_source(document_id, doc_type):
    return {
        "document_id": document_id,
        "doc_type": doc_type,
        "source_name": "test-fixture",
        "source_version": "0.1",
        "license": "synthetic-original",
        "is_synthetic": True,
        "classification": "synthetic_public",
        "created_on": date(2026, 10, 21),
    }


def make_candidate():
    return {
        "candidate_id": "cand-001",
        "headline": "Data analyst",
        "summary": "Analyst with experience in reporting and SQL.",
        "resume_text": "Data analyst. Built weekly sales reports with SQL and Excel.",
        "skills": ["SQL", "Excel"],
        "experience": [
            {
                "job_title": "Data Analyst",
                "organization": "Northwind Example Ltd",
                "start_year": 2021,
                "end_year": None,
                "description": "Built weekly sales reports.",
            }
        ],
        "source": make_source("cand-001", "candidate_profile"),
    }


def make_job():
    return {
        "job_id": "job-001",
        "title": "Data Analyst",
        "summary": "Analyst role on the sales team.",
        "description_text": "We need an analyst to build reports and answer questions.",
        "responsibilities": ["Build reports"],
        "must_have": [{"requirement_id": "job-001-r01", "text": "SQL"}],
        "nice_to_have": [{"requirement_id": "job-001-r02", "text": "Tableau"}],
        "source": make_source("job-001", "job_description"),
    }


def make_assessment():
    return {
        "assessment_id": "asm-001",
        "candidate_id": "cand-001",
        "job_id": "job-001",
        "assessment_type": "work_sample",
        "rubric_version": "r1",
        "criterion": "Writes correct SQL",
        "observed_evidence": "Wrote a join and a group by without help.",
        "reviewer_role": "synthetic reviewer",
        "assessed_on": date(2026, 10, 1),
        "source": make_source("asm-001", "assessment_record"),
    }


def make_chunk():
    return {
        "chunk_id": "cand-001#skills-00",
        "document_id": "cand-001",
        "doc_type": "candidate_profile",
        "section": "skills",
        "owner_id": "cand-001",
        "chunk_index": 0,
        "start_char": 0,
        "end_char": 40,
        "ingestion_version": "ing-0.1",
        "chunking_config_id": "size400-overlap50",
        "classification": "synthetic_public",
    }


def make_case():
    return {
        "case_id": "EV-0001",
        "split": "dev",
        "category": "exact_skill",
        "question": "Which profiles list SQL?",
        "expected_behavior": "answer",
        "corpus_requirements": "At least 2 profiles list SQL.",
    }


# DocumentSource


def test_document_source_valid():
    DocumentSource(**make_source("cand-001", "candidate_profile"))


def test_document_source_prefix_must_match_type():
    with pytest.raises(ValidationError):
        DocumentSource(**make_source("job-001", "candidate_profile"))


def test_real_data_cannot_be_synthetic_public():
    data = make_source("cand-001", "candidate_profile")
    data["is_synthetic"] = False
    data["license"] = "other"
    with pytest.raises(ValidationError):
        DocumentSource(**data)


def test_synthetic_license_needs_synthetic_flag():
    data = make_source("cand-001", "candidate_profile")
    data["is_synthetic"] = False
    data["classification"] = "restricted"
    with pytest.raises(ValidationError):
        DocumentSource(**data)


# CandidateProfile


def test_candidate_valid():
    CandidateProfile(**make_candidate())


def test_candidate_has_no_name_field():
    data = make_candidate()
    data["name"] = "Someone"
    with pytest.raises(ValidationError):
        CandidateProfile(**data)


def test_candidate_bad_id():
    data = make_candidate()
    data["candidate_id"] = "c1"
    with pytest.raises(ValidationError):
        CandidateProfile(**data)


def test_candidate_source_must_match_id():
    data = make_candidate()
    data["source"] = make_source("cand-002", "candidate_profile")
    with pytest.raises(ValidationError):
        CandidateProfile(**data)


def test_candidate_duplicate_skills_rejected():
    data = make_candidate()
    data["skills"] = ["SQL", "sql"]
    with pytest.raises(ValidationError):
        CandidateProfile(**data)


def test_experience_end_before_start_rejected():
    data = make_candidate()
    data["experience"][0]["end_year"] = 2015
    with pytest.raises(ValidationError):
        CandidateProfile(**data)


# JobDescription


def test_job_valid():
    JobDescription(**make_job())


def test_job_needs_a_must_have():
    data = make_job()
    data["must_have"] = []
    with pytest.raises(ValidationError):
        JobDescription(**data)


def test_job_requirement_id_must_match_job():
    data = make_job()
    data["must_have"][0]["requirement_id"] = "job-002-r01"
    with pytest.raises(ValidationError):
        JobDescription(**data)


def test_job_requirement_ids_must_be_unique():
    data = make_job()
    data["nice_to_have"][0]["requirement_id"] = "job-001-r01"
    with pytest.raises(ValidationError):
        JobDescription(**data)


# AssessmentRecord


def test_assessment_valid():
    AssessmentRecord(**make_assessment())


def test_assessment_has_no_score_field():
    data = make_assessment()
    data["score"] = 4
    with pytest.raises(ValidationError):
        AssessmentRecord(**data)


def test_assessment_bad_job_id():
    data = make_assessment()
    data["job_id"] = "J1"
    with pytest.raises(ValidationError):
        AssessmentRecord(**data)


# ChunkMetadata


def test_chunk_valid():
    ChunkMetadata(**make_chunk())


def test_chunk_id_must_start_with_document_id():
    data = make_chunk()
    data["chunk_id"] = "cand-002#skills-00"
    with pytest.raises(ValidationError):
        ChunkMetadata(**data)


def test_chunk_end_must_be_after_start():
    data = make_chunk()
    data["end_char"] = 0
    with pytest.raises(ValidationError):
        ChunkMetadata(**data)


# EvaluationCase


def test_case_valid():
    EvaluationCase(**make_case())


def test_case_bad_id():
    data = make_case()
    data["case_id"] = "case1"
    with pytest.raises(ValidationError):
        EvaluationCase(**data)


def test_draft_answer_needs_corpus_requirements():
    data = make_case()
    data["corpus_requirements"] = ""
    with pytest.raises(ValidationError):
        EvaluationCase(**data)


def test_refuse_needs_reason():
    data = make_case()
    data["expected_behavior"] = "refuse"
    with pytest.raises(ValidationError):
        EvaluationCase(**data)


def test_refuse_cannot_have_claims():
    data = make_case()
    data["expected_behavior"] = "refuse"
    data["refusal_reason"] = "pii_request"
    data["expected_claims"] = ["Something"]
    with pytest.raises(ValidationError):
        EvaluationCase(**data)


def test_required_citation_must_be_relevant():
    data = make_case()
    data["relevant_doc_ids"] = ["cand-001"]
    data["required_citation_doc_ids"] = ["cand-002"]
    with pytest.raises(ValidationError):
        EvaluationCase(**data)


def test_bound_answer_needs_ids_and_claims():
    data = make_case()
    data["status"] = "bound"
    with pytest.raises(ValidationError):
        EvaluationCase(**data)
