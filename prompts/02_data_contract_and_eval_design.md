# Shared execution contract

You are acting as a senior AI engineer and a patient technical mentor. Read the repository `README.md` first and inspect the current files before proposing changes. This project is the **Domain RAG Copilot: Candidate Workflow & Job-Fit Support**: a privacy-conscious, evidence-grounded RAG portfolio project using only synthetic / license-cleared data. It is decision support; it must never make hiring or rejection decisions.

Work only on the current stage. Preserve already-working code and interfaces. Do not rewrite unrelated modules, invent test results, fabricate metrics, or silently swap libraries/providers. Prefer small, typed, testable modules and simple interfaces. Do not add credentials or real candidate data. Keep secrets in environment variables and `.env` must be git-ignored.

Before coding, summarize the stage goal, the concepts I should learn, the current files/interfaces that matter, and the planned changes. If the repository state makes an essential detail unknowable, ask one focused question; otherwise choose a sensible default and document it. Then implement the stage.

At the end, provide: (1) a plain-language explanation, (2) changed-file list and purpose, (3) exact commands to run, (4) tests actually run and their honest results, (5) assumptions / limitations / privacy risks, and (6) a checkbox acceptance checklist plus a recommendation whether to proceed. Keep a `docs/` decision or design note when a meaningful architecture choice is made. Never claim production readiness just because the app runs locally.

---

# Stage 02 — Dataset selection, schemas, and evaluation design

## Goal
Decide what data will be used, define canonical schemas, and design a small, independent golden evaluation set before downloading or indexing any corpus.

## Tasks
1. Compare these source options and recommend the smallest effective path for the first release:
   - A fictional starter corpus of ~50 candidate profiles, 10–20 job descriptions, and a modest set of fictional assessment records.
   - ESCO occupation/skills classifications: https://esco.ec.europa.eu/en/use-esco/download
   - O*NET releases and database license: https://www.onetcenter.org/db_releases.html
   - Optional Hugging Face synthetic candidate/job matching dataset: https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic
2. Default to fictional records for the first end-to-end demonstration. Pick at most one canonical occupation/skills taxonomy based on the stated geographic scope; do not merge taxonomies without a documented crosswalk. Present benefits, limitations, license/attribution checks, storage size, and likely implementation effort.
3. For the optional Hugging Face corpus, inspect the dataset card and note its declared synthetic status, declared MIT license, configurations, and limitations. The card reports all examples in the `train` split and describes skill-overlap-based matching labels; therefore design a separate holdout test set and watch for simplistic or templated text. Do not treat the supplied labels as objective hiring truth.
4. Define Pydantic schemas for `CandidateProfile`, `JobDescription`, `AssessmentRecord`, `DocumentSource`, `ChunkMetadata`, and `EvaluationCase`. Include stable IDs, provenance, source/version fields, document type, section metadata, and data classification where relevant. Do not put unnecessary personal attributes in the schema.
5. Define a JSONL schema for `evals/golden_set.jsonl`, with expected relevant document/chunk IDs, evidence/claims, citation requirements, expected abstention behavior, category tags, and a stable case ID. Keep this file separate from the indexed corpus.
6. Create 60–100 planned evaluation cases over time; start with at least 20–30 labeled examples if that is manageable, including exact skill searches, paraphrases, cross-document questions, missing evidence, ambiguous evidence, conflicting records, injection instructions inside documents, unauthorized access, and PII requests. Reserve an explicit holdout subset.
7. Add `docs/dataset-card.md` template and `docs/data-governance.md` or equivalent describing consent/provenance, licensing, retention, redaction, Git handling, and source manifests.
8. Record the selected source plan in a short ADR. Do not download or index data yet.

## Acceptance criteria
- A written dataset decision explains exactly which data will be acquired/generated in Stage 03 and why.
- Schemas are explicit and validated by tests or example fixtures.
- Evaluation cases have stable IDs and clear relevance/citation/abstention expectations; evaluation data will not be indexed into the corpus.
- License and data-governance steps are documented. Explain how the evaluation set will prevent data leakage and metric cherry-picking.
