# Requirements

Project: Domain RAG Copilot, Candidate Workflow and Job-Fit Support (P7-016)
Status: Stage 00 draft, to be reviewed before Stage 01
Data rule: only fictional or license-cleared data. No real candidate records.

## 1. Purpose

The system lets a recruiter or hiring manager ask questions about approved job descriptions, candidate profiles and assessment records. It answers only from retrieved text and shows where each claim came from. It can also compare a job's listed requirements with the evidence in one candidate profile.

It is decision support. It never recommends hiring or rejecting anyone.

## 2. Personas

| Persona | What they do | What they need from the system |
|---|---|---|
| Recruiter | Searches approved records, for example "which profiles mention Python" | Fast search, short answers, a citation on every claim |
| Hiring manager | Checks one candidate against one job's requirements | A per-requirement view of supported, not found, and needs review, with sources |
| Reviewer / maintainer | Checks citations, runs evaluations, reads feedback and logs | Debug output, evaluation reports, failure logs, version records |
| Portfolio viewer | Opens the public demo | A working demo with clearly fictional data and visible limits |

## 3. User stories

| ID | Story |
|---|---|
| US-01 | As a recruiter, I ask a question about the approved corpus and get an answer with citations so I can open each source. |
| US-02 | As a recruiter, I get a clear "not enough evidence" reply when the documents do not answer my question, instead of a guess. |
| US-03 | As a hiring manager, I pick a job and a candidate and see each requirement marked supported, not found in supplied evidence, or needs human review. |
| US-04 | As a hiring manager, I see the exact text that supports each "supported" result. |
| US-05 | As a recruiter, I am refused when I ask the system to infer age, gender, ethnicity, religion, health or personality. |
| US-06 | As a reviewer, I see the retrieval ranks (dense, keyword, fused, reranked) for a query so I can find why an answer was wrong. |
| US-07 | As a reviewer, I run the evaluation suite and get a report that names the model, index, prompt and evaluation-set versions. |
| US-08 | As a reviewer, I mark a job-fit output as reviewed or disputed and leave a note. |
| US-09 | As a maintainer, I rebuild the index from the manifest and get the same chunk IDs. |
| US-10 | As a portfolio viewer, I can see that all data is fictional and read the limitations. |

## 4. Functional requirements

Each requirement has an ID, the stage that builds it, and a pass/fail check.

### 4.1 Data and ingestion

| ID | Requirement | Stage | Acceptance criterion |
|---|---|---|---|
| FR-01 | Validate candidate profiles, job descriptions and assessment records against typed schemas. | 02, 04 | A record with a missing required field is rejected with a reason. All committed sample records pass. |
| FR-02 | Keep provenance for every record: source, license or synthetic label, ingestion version. | 03, 04 | For any chunk ID, a lookup returns the source document ID and the ingestion version. |
| FR-03 | Detect and redact configured PII patterns (email, phone, government-style IDs, street addresses) before indexing. | 04, 10 | A test file with planted fake PII produces chunks, logs and index payloads that contain none of it. |
| FR-04 | Split documents into section-aware chunks with configurable size and overlap. Save the settings used for each index build. | 04 | Same input plus same settings gives identical chunk IDs on two runs. The index manifest lists the settings. |
| FR-05 | Store each chunk's section, document type, document ID, and owner scope (job ID or candidate ID) as metadata. | 04 | Every chunk in a test build has all five metadata fields. |

### 4.2 Retrieval

| ID | Requirement | Stage | Acceptance criterion |
|---|---|---|---|
| FR-06 | Create embeddings once and store them in a persistent vector index. | 05 | Restarting the app and querying makes zero embedding calls for existing chunks. |
| FR-07 | Dense retrieval returns the top K chunks for a query. | 05 | Recall@K and MRR are computed on the evaluation set and written to a report. |
| FR-08 | Keyword retrieval with BM25, combined with dense results by reciprocal rank fusion. | 06 | The hybrid result is compared with the dense baseline on the same evaluation set. |
| FR-09 | A cross-encoder reranks the fused candidate pool. | 06 | The final ranking is compared with the fused ranking on the same set. Debug output shows all four ranks per chunk. |
| FR-10 | Retrieval accepts a scope filter (job ID, candidate ID, document type) and applies it inside the search, not after. | 05, 06 | A query scoped to candidate A never returns a chunk owned by candidate B, tested with a query that names B. |

### 4.3 Answers and job-fit

| ID | Requirement | Stage | Acceptance criterion |
|---|---|---|---|
| FR-11 | Generate answers only from retrieved chunks and attach citations to chunk IDs. | 07 | Every cited ID exists in the retrieved set. An answer with an unknown ID is rejected by the validator. |
| FR-12 | When retrieved evidence is not enough, return an insufficient-evidence result with the reason. | 07 | On evaluation cases marked abstain-expected, the abstention rate is measured and reported. |
| FR-13 | Treat text inside documents as data. Instructions inside a document do not change system behavior. | 07, 10 | Planted instructions in a test resume ("ignore previous rules") do not change the output format or leak the system prompt. |
| FR-14 | Refuse requests to infer protected or sensitive traits or personality, and refuse requests for personal identifiers. | 07, 10 | A set of refusal test prompts all return a refusal with no inferred trait. |
| FR-15 | Job-fit comparison takes one job and one candidate and labels each must-have and nice-to-have requirement as `supported`, `not_found_in_supplied_evidence`, or `needs_human_review`. | 08 | Each `supported` item has at least one valid citation. The output has no overall score, rank, or hire/reject wording. |
| FR-16 | Every job-fit output includes a notice that a qualified human must review the sources. | 08, 13 | A test checks the notice is present in the API response and in the UI. |
| FR-17 | The job-fit service never states that a skill is absent. | 08 | A test with a skill missing from the profile returns `not_found_in_supplied_evidence`, and the wording check finds no "does not have" phrasing. |

### 4.4 Evaluation, API, operations

| ID | Requirement | Stage | Acceptance criterion |
|---|---|---|---|
| FR-18 | Keep a curated evaluation set, separate from the corpus, with a holdout part. | 02, 09 | The index build fails if an evaluation file is found in the corpus path. The holdout is not used in tuning runs. |
| FR-19 | Report Recall@K, MRR, answer correctness, groundedness, citation correctness, abstention quality, job-fit classification accuracy and F1, latency, and cost estimate. | 09 | One command produces a report with all listed metrics and the version of every component. |
| FR-20 | Typed HTTP API with request validation, error responses, health check and generated OpenAPI docs. | 11 | Integration tests cover the success path and each defined error. `/health` returns 200 when dependencies are up. |
| FR-21 | Access control: a caller can only use records inside their allowed scope. | 10, 11 | Changing an ID in a request to one outside the caller's scope returns 403 or 404 and no data. |
| FR-22 | Structured logs record IDs, timings, scores and errors. They do not record full document text by default. | 12 | A log test greps a run's logs for planted document text and finds none. |
| FR-23 | Store reviewer feedback (reviewed, disputed, note) linked to the output ID. | 12 | A feedback record can be written and read back through the API. |
| FR-24 | Web interface for recruiters and hiring managers with clickable citations, an abstention view, the human-review notice, and a visible "fictional data" label. | 13 | A manual checklist plus browser tests cover each listed element. |

## 5. Non-functional requirements

| ID | Area | Requirement | Check |
|---|---|---|---|
| NFR-01 | Privacy | Public repo and demo contain only fictional or license-cleared data. | Data manifest lists a license or "synthetic" for every file. `.env` and `data/raw` are git-ignored. |
| NFR-02 | Security | Secrets come from environment variables only. | A scan of the repo finds no keys. App fails at startup if a required setting is missing. |
| NFR-03 | Reproducibility | Dependencies are pinned. Model names and index settings are recorded in every report. | Reports contain a version block. A fresh checkout builds the same index. |
| NFR-04 | Portability | The LLM provider and the embedding model can be changed by configuration. | A fake provider is used in unit tests. Switching needs no code change outside the provider module. |
| NFR-05 | Testability | Each component can be tested without network access using fakes. | Unit tests run offline in CI. |
| NFR-06 | Latency | p50 and p95 latency are measured per stage. Targets are set after the first baseline. | Report includes the numbers. No target is claimed before measurement. |
| NFR-07 | Cost | Token counts and estimated cost per request are recorded. | Report includes cost per request and per evaluation run. |
| NFR-08 | Honesty | Reports include negative results and limits. | Review checklist item at each stage. |
| NFR-09 | Accessibility | The Stage 13 interface supports keyboard use and readable contrast. | Manual checklist, with an automated accessibility scan if time allows. |
| NFR-10 | Maintainability | Components sit behind small interfaces (see architecture.md section 6). | Swapping a fake for the real component needs no change in callers. |

## 6. Out of scope

- Automatic rejecting, shortlisting, scoring or ranking of candidates as a final decision.
- Ranking candidates against each other by fit. Search results are ranked by relevance to the question only.
- Inferring protected traits, personality, health, or other personal attributes.
- Real resumes, scraped personal data, or any data without permission.
- Training a foundation model.
- Claims of legal compliance, fairness certification, or production readiness.
- Multi-tenant enterprise features such as single sign-on, billing, or per-organization encryption keys.

## 7. Assumptions

| ID | Assumption | Where it gets confirmed |
|---|---|---|
| A-01 | The first corpus is about 50 fictional profiles, 10 to 20 job descriptions and a small set of assessment records. | Stage 02 |
| A-02 | English only for the first version. | Stage 02 |
| A-03 | One job and one candidate at a time for job-fit. | Stage 08 |
| A-04 | A simple role-based token or API key is enough for the demo. Real identity management is out of scope. | Stage 10 |
| A-05 | The LLM provider is a hosted API. The choice is made in Stage 07 and stays configurable. | Stage 07 |
| A-06 | PostgreSQL is added only when feedback and audit records need it. | Stage 12 |

## 8. Stage gates

The order below matches the README table. Stage 13 is last.

| Stage | Name | Gate |
|---|---|---|
| 00 | Scope and architecture | These docs reviewed and approved |
| 01 | Repository scaffold | Lint, format, test baseline and settings pass |
| 02 | Data contract and evaluation design | Dataset choice and schemas approved, evaluation cases drafted |
| 03 | Dataset onboarding | Data validated, manifest and data card written |
| 04 | Ingestion and chunking | Ingestion tests pass, chunk IDs deterministic |
| 05 | Embeddings and dense retrieval | Baseline Recall@K and MRR measured |
| 06 | Hybrid search and reranking | Comparison with the dense baseline reported |
| 07 | Grounded RAG and citations | Citation validator, abstention and injection tests pass |
| 08 | Job-fit evidence comparison | Job-fit tests pass, no hire/reject output |
| 09 | Evaluation suite | One command produces the full report |
| 10 | Responsible AI, privacy, security | Threat model written, access and redaction tests pass |
| 11 | FastAPI integration | API tests pass, OpenAPI docs generated |
| 12 | Observability, CI, release | CI green, logs and feedback working |
| 13 | Full-stack website and deployment | Deployed demo, built on the tested backend |
