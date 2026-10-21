from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ID formats. These are fixed in Stage 02 so that the golden set can use them.
CANDIDATE_ID = r"^cand-\d{3}$"
JOB_ID = r"^job-\d{3}$"
ASSESSMENT_ID = r"^asm-\d{3}$"
DOCUMENT_ID = r"^(cand|job|asm)-\d{3}$"
REQUIREMENT_ID = r"^job-\d{3}-r\d{2}$"
CHUNK_ID = r"^(cand|job|asm)-\d{3}#[a-z_]+-\d{2}$"
CASE_ID = r"^EV-\d{4}$"

CandidateIdStr = Annotated[str, Field(pattern=CANDIDATE_ID)]
JobIdStr = Annotated[str, Field(pattern=JOB_ID)]
DocumentIdStr = Annotated[str, Field(pattern=DOCUMENT_ID)]
ChunkIdStr = Annotated[str, Field(pattern=CHUNK_ID)]

DocType = Literal["candidate_profile", "job_description", "assessment_record"]
Classification = Literal["synthetic_public", "licensed_public", "restricted"]

PREFIX_BY_DOC_TYPE = {
    "candidate_profile": "cand",
    "job_description": "job",
    "assessment_record": "asm",
}


class StrictModel(BaseModel):
    # Unknown fields are errors, so a typo in a field name is caught.
    model_config = ConfigDict(extra="forbid")


class DocumentSource(StrictModel):
    """Where a document came from. One record is one document in version 1."""

    document_id: str = Field(pattern=DOCUMENT_ID)
    doc_type: DocType
    source_name: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    license: Literal["synthetic-original", "CC-BY-4.0", "MIT", "other"]
    is_synthetic: bool
    classification: Classification
    created_on: date
    checksum_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    notes: str = ""

    @model_validator(mode="after")
    def check_source(self):
        prefix = PREFIX_BY_DOC_TYPE[self.doc_type]
        if not self.document_id.startswith(prefix + "-"):
            raise ValueError("document_id prefix does not match doc_type")
        if self.license == "synthetic-original" and not self.is_synthetic:
            raise ValueError("license synthetic-original needs is_synthetic = true")
        if self.classification == "synthetic_public" and not self.is_synthetic:
            raise ValueError("only synthetic data can be synthetic_public")
        return self


class ExperienceEntry(StrictModel):
    job_title: str = Field(min_length=2)
    organization: str = Field(min_length=2)  # a fictional company name
    start_year: int = Field(ge=1980, le=2100)
    end_year: int | None = Field(default=None, ge=1980, le=2100)  # None = current
    description: str = Field(min_length=10)

    @model_validator(mode="after")
    def check_years(self):
        if self.end_year is not None and self.end_year < self.start_year:
            raise ValueError("end_year is before start_year")
        return self


class CandidateProfile(StrictModel):
    """A fictional candidate. There is no name, age, gender or address field."""

    candidate_id: str = Field(pattern=CANDIDATE_ID)
    headline: str = Field(min_length=3)
    summary: str = Field(min_length=10)
    resume_text: str = Field(min_length=50)
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    # True only for the one test profile that holds fake contact details.
    has_planted_test_pii: bool = False
    source: DocumentSource

    @model_validator(mode="after")
    def check_profile(self):
        if self.source.document_id != self.candidate_id:
            raise ValueError("source.document_id must equal candidate_id")
        if self.source.doc_type != "candidate_profile":
            raise ValueError("source.doc_type must be candidate_profile")
        lowered = [skill.strip().lower() for skill in self.skills]
        if "" in lowered:
            raise ValueError("a skill is empty")
        if len(lowered) != len(set(lowered)):
            raise ValueError("skills contain duplicates")
        if self.has_planted_test_pii and not self.source.is_synthetic:
            raise ValueError("planted test PII is only allowed in synthetic data")
        return self


class Requirement(StrictModel):
    requirement_id: str = Field(pattern=REQUIREMENT_ID)
    text: str = Field(min_length=3)
    skill: str | None = None  # the main skill named in the text, if there is one


class JobDescription(StrictModel):
    job_id: str = Field(pattern=JOB_ID)
    title: str = Field(min_length=3)
    summary: str = Field(min_length=10)
    description_text: str = Field(min_length=50)
    responsibilities: list[str] = Field(default_factory=list)
    must_have: list[Requirement] = Field(min_length=1)
    nice_to_have: list[Requirement] = Field(default_factory=list)
    source: DocumentSource

    @model_validator(mode="after")
    def check_job(self):
        if self.source.document_id != self.job_id:
            raise ValueError("source.document_id must equal job_id")
        if self.source.doc_type != "job_description":
            raise ValueError("source.doc_type must be job_description")
        ids = [req.requirement_id for req in self.must_have + self.nice_to_have]
        if len(ids) != len(set(ids)):
            raise ValueError("requirement ids are not unique")
        for requirement_id in ids:
            if not requirement_id.startswith(self.job_id + "-"):
                raise ValueError("requirement id does not match job_id")
        return self


class AssessmentRecord(StrictModel):
    """Notes about one criterion. There is no numeric score on purpose."""

    assessment_id: str = Field(pattern=ASSESSMENT_ID)
    candidate_id: str = Field(pattern=CANDIDATE_ID)
    job_id: str | None = Field(default=None, pattern=JOB_ID)
    assessment_type: Literal["work_sample", "structured_interview", "skills_exercise"]
    rubric_version: str = Field(min_length=1)
    criterion: str = Field(min_length=3)
    observed_evidence: str = Field(min_length=10)
    reviewer_role: str = Field(min_length=3)  # a role, not a person's name
    assessed_on: date
    caveats: str = ""
    source: DocumentSource

    @model_validator(mode="after")
    def check_assessment(self):
        if self.source.document_id != self.assessment_id:
            raise ValueError("source.document_id must equal assessment_id")
        if self.source.doc_type != "assessment_record":
            raise ValueError("source.doc_type must be assessment_record")
        return self


class ChunkMetadata(StrictModel):
    chunk_id: str = Field(pattern=CHUNK_ID)
    document_id: str = Field(pattern=DOCUMENT_ID)
    doc_type: DocType
    section: str = Field(pattern=r"^[a-z_]+$")
    # The job or candidate that owns the chunk. Scope filters use this.
    owner_id: str = Field(pattern=r"^(cand|job)-\d{3}$")
    chunk_index: int = Field(ge=0)
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=1)
    ingestion_version: str = Field(min_length=1)
    chunking_config_id: str = Field(min_length=1)
    classification: Classification

    @model_validator(mode="after")
    def check_chunk(self):
        if not self.chunk_id.startswith(self.document_id + "#"):
            raise ValueError("chunk_id must start with document_id and #")
        prefix = PREFIX_BY_DOC_TYPE[self.doc_type]
        if not self.document_id.startswith(prefix + "-"):
            raise ValueError("document_id prefix does not match doc_type")
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be larger than start_char")
        return self


Category = Literal[
    "exact_skill",
    "paraphrase",
    "multi_document",
    "missing_evidence",
    "ambiguous_evidence",
    "conflicting_records",
    "prompt_injection",
    "unauthorized_access",
    "pii_request",
    "protected_trait",
    "hiring_decision",
    "job_fit",
]

RefusalReason = Literal[
    "not_found_in_supplied_evidence",
    "out_of_scope_access",
    "pii_request",
    "protected_trait",
    "hiring_decision",
    "ranking_request",
]


class EvalScope(StrictModel):
    """What the caller in a test case is allowed to read."""

    candidate_ids: list[CandidateIdStr] = Field(default_factory=list)
    job_ids: list[JobIdStr] = Field(default_factory=list)


class EvaluationCase(StrictModel):
    case_id: str = Field(pattern=CASE_ID)
    split: Literal["dev", "holdout"]
    category: Category
    # draft: the corpus does not exist yet. bound: ids checked against the corpus.
    status: Literal["draft", "bound", "reviewed"] = "draft"
    question: str = Field(min_length=5)
    # None means no restriction. An object means only these records are allowed.
    allowed_scope: EvalScope | None = None
    expected_behavior: Literal["answer", "abstain", "refuse"]
    refusal_reason: RefusalReason | None = None
    relevant_doc_ids: list[DocumentIdStr] = Field(default_factory=list)
    relevant_chunk_ids: list[ChunkIdStr] = Field(default_factory=list)
    reference_evidence: list[str] = Field(default_factory=list)
    expected_claims: list[str] = Field(default_factory=list)
    required_citation_doc_ids: list[DocumentIdStr] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    expects_uncertainty: bool = False
    corpus_requirements: str = ""
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def check_case(self):
        extra = set(self.required_citation_doc_ids) - set(self.relevant_doc_ids)
        if extra:
            raise ValueError("required citations must be in relevant_doc_ids")

        if self.expected_behavior == "answer":
            if self.refusal_reason is not None:
                raise ValueError("an answer case has no refusal_reason")
            if self.status == "draft" and not self.corpus_requirements:
                raise ValueError("a draft answer case needs corpus_requirements")
            if self.status != "draft":
                if not self.relevant_doc_ids or not self.expected_claims:
                    raise ValueError("bound answer cases need ids and claims")
        else:
            if self.refusal_reason is None:
                raise ValueError("abstain and refuse cases need a refusal_reason")
            if self.expected_claims or self.required_citation_doc_ids:
                raise ValueError("abstain and refuse cases have no claims or citations")
        return self
