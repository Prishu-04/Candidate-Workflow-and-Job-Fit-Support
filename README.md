# Domain RAG Copilot: Candidate Workflow & Job-Fit Support

> A portfolio-grade, evidence-grounded RAG application for recruiter and hiring-manager research. It searches approved candidate profiles, job descriptions, and structured assessment records, answers questions with traceable citations, and explains documented skill alignment and missing evidence. It is **decision support, not an automated hiring decision-maker**.

## 1. Project overview

Recruiters and hiring managers often need to search many documents, compare a job's stated requirements with evidence in a candidate profile, and trace each claim back to a source. This project demonstrates how to build that workflow with retrieval-augmented generation (RAG), rather than asking an LLM to guess from its general knowledge.

### Primary users

- **Recruiter:** asks questions about approved candidate records and job descriptions, such as which documented examples mention Python or customer research.
- **Hiring manager:** reviews evidence associated with listed job requirements and identifies which requirements are supported, unsupported, or unclear in the supplied documents.
- **Reviewer / project maintainer:** checks citations, evaluates quality, reviews feedback, and monitors reliability.

### Core user journeys

1. Load permitted sample documents and structured records.
2. Ask a question about an approved job or candidate profile.
3. Retrieve evidence using semantic and keyword search, then rerank it.
4. Generate an answer only from retrieved evidence, with source citations and a clear abstention when evidence is inadequate.
5. Compare a job's stated skills with evidence documented in a candidate profile. Explain matches, gaps, and uncertainty; do not recommend hiring or rejection.
6. Review evaluation metrics, failures, latency, cost estimates, and feedback.

### What this project is not

- It is not an autonomous hiring, rejection, eligibility, or performance-prediction system.
- It must not infer protected or sensitive characteristics, personality, health, ethnicity, religion, age, gender, or other personal traits.
- It must not treat a missing mention as proof that a candidate lacks a skill.
- It must not claim that a candidate is objectively suitable based on a synthetic match label or a single numeric similarity score.
- It is not a compliance certification. Real-world use with real candidate data would require a separate legal, privacy, security, accessibility, and organizational review.

## 2. Architecture at a glance

The intended production-style flow is shown below. The RAG answer path and the job-fit evidence path share validated source data and retrieval infrastructure, but job-fit comparison should be implemented as a separate, testable service instead of embedding arbitrary scoring logic in a prompt.

```mermaid
flowchart TD
    A[Approved source data: fictional resumes, job descriptions, structured assessments, optional skills taxonomy] --> B[Ingestion: validate schema, document consent/provenance, redact PII, normalize]
    B --> C[Canonical records and data lineage]
    C --> D[Parse and section-aware chunking with metadata]
    D --> E[Embedding model]
    E --> F[(Qdrant vector index)]
    D --> G[BM25 keyword index]
    F --> H[Hybrid retrieval and reciprocal-rank fusion]
    G --> H
    H --> I[Cross-encoder reranker]
    I --> J{Enough relevant evidence?}
    J -->|Yes| K[LLM generation grounded only in retrieved context]
    J -->|No| L[Abstain, explain evidence gap, or ask a clarification]
    K --> M[Validate source IDs, citations, schema, and guardrails]
    L --> M
    C --> N[Job-fit evidence comparison]
    N --> O[Supported / not found / unclear requirement evidence]
    O --> P[Human review; no automatic hiring decision]
    M --> Q[FastAPI application API and access control]
    P --> Q
    Q --> R[Next.js recruiter and hiring-manager interface]
    Q --> S[Structured logs, latency/cost metrics, feedback]
    T[Curated golden evaluation set] --> U[Retrieval, answer, citation, refusal, safety evaluation]
    U --> V[Improve chunking, retrieval, prompts, and models]
    V -. regression test .-> T
```

An editable Mermaid version is also available at [`docs/project-flow.mmd`](docs/project-flow.mmd), and a rendered PNG is at [`docs/project-flow.png`](docs/project-flow.png).

## 3. Recommended technology choices

Use one implementation per layer and keep components behind simple interfaces so they can be replaced without rebuilding the whole application.

| Layer | Default choice | Why it is here |
|---|---|---|
| Language | Python | Data processing, retrieval, API, evaluation, and tests |
| RAG utilities | LangChain selectively | Reusable document/splitter/retriever integrations; keep core behavior explicit and testable |
| Document and schema validation | Pydantic + Python parsers | Validate records and make data contracts explicit |
| Local embeddings | Sentence Transformers | Reproducible baseline embeddings without a per-call API fee; model quality and hardware requirements still need evaluation |
| Vector database | Qdrant | Persistent vector index and a clear local-to-hosted path |
| Keyword retrieval | BM25 | Helps with exact skill names, acronyms, and rare terms |
| Rank fusion | Reciprocal Rank Fusion (RRF) | Combines keyword and semantic result rankings without assuming their raw scores are comparable |
| Reranking | Sentence Transformers cross-encoder | Reranks a small candidate pool using query-document relevance |
| Generation | Configurable LLM provider API | Keep the provider/model configurable; secrets stay in environment variables |
| Backend | FastAPI + Pydantic | Typed endpoints and API schema |
| App data / audit metadata | PostgreSQL | Optional until persistence, user management, or audit records are needed |
| Frontend | Next.js + TypeScript + Tailwind CSS | Recruiter-facing interface built only in the final stage |
| Tests | pytest | Unit, integration, API, and regression tests |
| Observability | Structured logs + basic metrics | Track retrieval and generation quality, latency, failures, and cost estimates |
| Packaging | Docker / Docker Compose | Repeatable local environment and deployable services |

**Important:** model names, package versions, endpoints, provider limits, and hosting free tiers change. Ask the coding assistant to verify current package documentation when implementation begins, pin tested versions, and document model versions in the repository. Do not silently upgrade dependencies or change providers during a stage.

## 4. Data strategy: when datasets should be introduced

**Do not download a large dataset at the start.** First finish Stage 00 and Stage 01 so the scope, interfaces, repository, environment, and tests are clear. Use Stage 02 to choose the source data and define schemas and evaluation cases. Bring the actual data in during Stage 03, when there is a validation/normalization plan.

### Data-source recommendations

1. **A small fictional starter corpus (required for the first working version).** Create about 50 fictional candidate profiles, 10–20 fictional job descriptions, and a small set of fictional structured assessment records. Include realistic variation and edge cases. This keeps the first end-to-end pipeline understandable and avoids putting real personal data in a portfolio repository. Clearly label everything synthetic.
2. **ESCO occupation and skills classification (optional taxonomy).** The European Commission makes ESCO classification packages downloadable in CSV, ODS, and RDF formats, including multilingual options. Use selected occupation/skill terms as a controlled vocabulary only after reviewing the current data and applicable terms. Official source: <https://esco.ec.europa.eu/en/use-esco/download>.
3. **O*NET database (optional U.S.-focused taxonomy).** The O*NET Resource Center lists the current production database as release 31.0 (August 2026) and links to its database license. It includes occupation-related data that can help normalize occupation and skills language. Review the current license and attribution requirements before redistribution. Official source: <https://www.onetcenter.org/db_releases.html>.
4. **Candidate-Job Matching Synthetic Dataset (optional larger benchmark).** The Hugging Face dataset card for <https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic> describes synthetic resumes, job postings, and match records, and declares an MIT license. The card reports that all examples are in the `train` split and describes rule-based skill-overlap labels. Inspect the actual configurations, schema, license, generation artifacts, and label methodology before use. Do **not** treat those labels as objective ground truth; create a separate, manually reviewed test set and split carefully to prevent resume/job leakage.

### Recommended starting choice

Start with the fictional corpus plus a curated evaluation set. Then optionally add **one** taxonomy (ESCO for a broader multilingual / European framing, or O*NET for a U.S.-focused framing). Only add the larger Hugging Face synthetic benchmark after the core pipeline works. Do not merge ESCO and O*NET identifiers or definitions without an explicit crosswalk.

### Data files and records

Keep raw downloads out of public Git by default. A recommended layout:

```text
data/
  raw/          # downloaded source data; git-ignored
  processed/    # normalized records; git-ignored if large/sensitive
  samples/      # tiny, fictional, license-cleared examples safe to commit
  manifests/    # source URL, version, retrieval date, license, checksum, transformation notes
```

Suggested canonical entities:

- **CandidateProfile:** stable candidate ID, fictional résumé text, documented skills, experience entries, source document IDs, provenance, and data classification.
- **JobDescription:** stable job ID, role/title, description, responsibilities, must-have requirements, nice-to-have requirements, and source/provenance fields.
- **AssessmentRecord:** assessment type, rubric version, documented criterion, observed evidence, reviewer/source, timestamp, and caveats. Use synthetic content for this portfolio project.
- **Chunk:** chunk ID, document ID, candidate/job association where permitted, document type, section, offsets or page references, source metadata, ingestion version, and text.
- **EvaluationCase:** question, allowed corpus scope, relevant document/chunk IDs, reference evidence, expected claims, required citations, and whether a safe abstention is expected.

### Ground-truth / evaluation dataset

Create this during Stage 02; use it throughout development. Begin with around 60–100 carefully curated test cases, not automatically generated test queries only. Cover exact skill lookups, semantic paraphrases, multi-document questions, conflicting or stale evidence, missing evidence, ambiguous requests, prompt injection in source documents, PII requests, and unsupported claims. Keep a holdout test set that is not used repeatedly to tune prompts. Store the evaluation set separately from the retrieval corpus.

## 5. Functional requirements

### Required

- Ingest and validate job descriptions, fictional candidate profiles, and structured assessment records.
- Preserve document IDs, section metadata, source provenance, and stable citations from output back to retrieved chunks.
- Support configurable chunk size/overlap and record the configuration used to build an index.
- Generate and persist embeddings; do not recompute them for every question.
- Support semantic retrieval, then hybrid retrieval using BM25 + dense retrieval and a documented rank-fusion strategy.
- Rerank retrieved candidates and expose the final ranked evidence in debug/evaluation output.
- Generate grounded answers with citations, uncertainty, and safe abstention for insufficient evidence.
- Compare stated job requirements with documented candidate evidence, distinguishing **supported**, **not found in supplied evidence**, and **ambiguous/needs human review**.
- Provide a typed backend API, automated tests, repeatable local startup, and a deployed interface at the final stage.
- Include quality measurements for retrieval, citations, groundedness, answer relevance, refusal behavior, latency, and cost estimates.
- Include a risk register, dataset card, known limitations, and human-review workflow.

### Out of scope for the portfolio build

- Automatically rejecting, shortlisting, scoring, or ranking candidates as a final hiring decision.
- Inferring personality or protected/sensitive traits from documents.
- Scraping personal résumés or real candidate records without permission.
- Training a new foundation model or claiming that model evaluation demonstrates lack of bias.

## 6. Project stages and completion gates

Run prompts in order, one stage at a time. Do not continue merely because code was generated; continue after tests and acceptance criteria pass. The individually copyable prompts are in [`prompts/`](prompts/).

| Stage | Prompt file | Main output / gate |
|---|---|---|
| 00 | `00_scope_and_architecture.md` | Requirements, assumptions, architecture decisions, acceptance criteria. No production code yet. |
| 01 | `01_repository_scaffold.md` | Clean repository, dependency management, settings, logging, lint/format, test baseline, Docker scaffold. |
| 02 | `02_data_contract_and_eval_design.md` | Approved data-source choice, canonical schemas, data manifest policy, curated evaluation set design and initial cases. **Choose datasets here.** |
| 03 | `03_dataset_onboarding.md` | Download/generate/validate the selected small dataset, data card, provenance manifest, safe samples, quality report. **Provide actual data here.** |
| 04 | `04_ingestion_and_chunking.md` | Deterministic parsing, normalization, metadata-rich chunks, ingestion tests. |
| 05 | `05_embeddings_and_dense_retrieval.md` | Embeddings, persistent Qdrant index, dense retrieval baseline, Recall@K/MRR measurement. |
| 06 | `06_hybrid_search_and_reranking.md` | BM25 + dense retrieval, rank fusion, reranker, comparison with dense baseline. |
| 07 | `07_grounded_rag_and_citations.md` | Grounded answer synthesis, citation schema/validation, abstention and prompt-injection resistance tests. |
| 08 | `08_job_fit_evidence_comparison.md` | Requirement-to-evidence comparison, evidence gaps/uncertainty, explanation format, no automated hiring decision. |
| 09 | `09_evaluation_suite.md` | Automated offline evaluation for retrieval, answer quality, grounding, citations, refusal, latency, and cost. |
| 10 | `10_responsible_ai_privacy_security.md` | Threat model, redaction, auth/authorization requirements, data retention, prompt injection and responsible-use controls. |
| 11 | `11_fastapi_api_integration.md` | Typed API, endpoints, request validation, error handling, integration tests and OpenAPI documentation. |
| 12 | `12_observability_ci_and_release.md` | Structured logs, feedback records, metrics, CI, containers, deployment readiness and reproducibility notes. |
| **13 — final** | `13_full_stack_website_and_deployment.md` | Build and deploy the full-stack recruiter-facing website using the already-tested backend. This is the final build prompt. |

## 7. Evaluation and success metrics

Report measured results, including negative results and limitations. Do not invent benchmark numbers or claim that a metric proves the system is fair or suitable for hiring.

| Area | Metric / check | What it tells you |
|---|---|---|
| Retrieval | Recall@K, MRR, optionally nDCG@K | Whether relevant evidence is retrieved and ranked usefully |
| Answer quality | Reference-based correctness and answer relevance | Whether the answer addresses the question accurately |
| Grounding | Claim support / groundedness review | Whether substantive answer claims are supported by retrieved evidence |
| Citations | Citation correctness and citation coverage | Whether each material claim points to the correct source chunk/document |
| Abstention | Safe-refusal / insufficient-evidence tests | Whether unsupported requests are handled correctly |
| Job-fit evidence | Requirement coverage, evidence attribution, uncertainty classification | Whether comparisons are faithful to supplied evidence—not whether someone should be hired |
| Reliability | Error rate and p50/p95 latency | Whether the system works consistently and promptly |
| Cost | Estimated tokens and model/vector-service cost per request | Whether operating cost is understood |
| Safety | Prompt-injection tests, unauthorized access tests, PII checks, deletion checks | Whether obvious privacy/security failures are caught |

Set target thresholds only after running a baseline. For a small curated corpus, a target such as Recall@5 ≥ 0.80 can be a useful initial goal, but actual performance depends on your data and query set. Record the model, embedding version, chunking settings, index version, reranker, prompt version, and evaluation-set version for every comparison.

## 8. Responsible AI, privacy, and human review

- Use synthetic data for the publicly shared demo. Never commit real CVs, personal identifiers, API keys, `.env` files, or unredacted assessment notes.
- Separate user identity/access logic from document retrieval. Do not allow a caller to retrieve another tenant's or candidate's records by changing an ID.
- Treat every source document as untrusted text. Instructions inside a résumé or job description are data, not commands for the assistant.
- Do not use protected or sensitive attributes—or obvious proxies—to generate candidate-fit conclusions.
- Never describe an unmentioned skill as definitively absent. Say that it was **not found in the supplied evidence**.
- Every job-fit output should include a reminder that a qualified human must review source evidence and apply the organization's approved hiring process.
- Log IDs, timings, scores, and error information where practical, not complete résumé text by default. Define retention and deletion behavior before using non-synthetic data.
- Provider APIs may receive prompts and retrieved text. With real candidate records, obtain explicit authorization and confirm provider retention / training / processing terms before sending personal data off-system.
- Use NIST AI RMF as a risk-management reference, not as a certification: <https://www.nist.gov/itl/ai-risk-management-framework>.

## 9. Suggested repository structure

```text
.
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── backend/
│   └── app/
│       ├── api/             # FastAPI routers and request/response models
│       ├── core/            # settings, logging, provider interfaces
│       ├── data/            # schemas and data validation
│       ├── ingestion/       # loaders, parsing, redaction, chunking
│       ├── retrieval/       # dense, BM25, fusion, reranking
│       ├── generation/      # prompts, grounded answer synthesis, citations
│       ├── job_fit/         # requirement-to-evidence comparisons
│       ├── evaluation/      # metrics and offline evaluation runner
│       ├── security/        # access checks, input/output safety
│       └── main.py
├── tests/                   # unit, integration, API, safety and regression tests
├── data/
│   ├── raw/                 # git-ignored
│   ├── processed/           # git-ignored as needed
│   ├── samples/             # tiny synthetic demo data only
│   └── manifests/
├── evals/
│   ├── golden_set.jsonl     # curated evaluation cases; do not index as corpus
│   └── reports/
├── scripts/                 # ingestion, evaluation, maintenance commands
├── docs/
│   ├── architecture.md
│   ├── project-flow.mmd
│   ├── project-flow.png
│   ├── dataset-card.md
│   ├── evaluation-report.md
│   ├── risk-register.md
│   └── decisions/            # short architecture decision records
├── prompts/                 # prompts for this staged build
└── frontend/                # created in final Stage 13
```

This is a target structure, not a requirement to create every file on day one. Each stage should add only the parts it needs.

## 10. Environment and secret handling

Provide `.env.example` with non-secret placeholders, such as:

```dotenv
APP_ENV=development
LOG_LEVEL=INFO
LLM_PROVIDER=replace_me
LLM_MODEL=replace_me
LLM_API_KEY=
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
DATABASE_URL=postgresql://user:password@localhost:5432/domain_rag_copilot
FRONTEND_ORIGIN=http://localhost:3000
```

Use settings validation at startup. Keep `.env` out of version control. Do not embed secrets in prompts, screenshots, logs, client-side JavaScript, or example notebooks. If a service can be used locally without a credential, make that the default development path.

## 11. How to use the prompts with an AI coding tool

1. Create an empty Git repository and save this README at the root before asking for code.
2. Open the repository in your preferred coding tool, or upload the README and existing project files if the tool cannot inspect the repository directly.
3. Start with `prompts/00_scope_and_architecture.md`. Ask the tool to explain its plan before implementation, and review assumptions.
4. Run only one stage prompt at a time. Ask for file-by-file explanations, commands to run, test results, and an acceptance checklist at every stage.
5. Run the code and tests yourself. Do not accept a claim that tests passed unless the tool actually ran them or you ran them locally.
6. Commit a working stage before proceeding, for example `git add . && git commit -m "stage 04 ingestion and chunking"`.
7. If a stage fails, ask the tool to debug the smallest failing case. Do not jump ahead or rewrite unrelated stages.
8. At Stage 02, choose the dataset strategy. At Stage 03, supply the selected dataset file(s) or let the coding tool retrieve official, license-cleared sources. Review license terms and data contents yourself.
9. Use Stage 13 **last**, after the API, tests, evaluation, security boundaries, and release setup are demonstrably working.

### What every stage should hand back

- A plain-language explanation of concepts and design decisions.
- A list of files created or changed, with the reason for each.
- Exact setup/run/test commands for your operating system or shell.
- Test output or an honest statement of what was not run.
- Known limitations, security/privacy implications, and assumptions.
- A clear acceptance checklist and a recommendation to proceed or fix issues first.

## 12. Portfolio / resume completion checklist

Before publishing the project, ensure you can demonstrate:

- [ ] A clear README, architecture diagram, setup instructions, and reproducible Docker workflow.
- [ ] Data source/version/license manifest and a statement that public demo data is synthetic or otherwise cleared for use.
- [ ] Dense baseline vs hybrid retrieval vs reranked retrieval comparison.
- [ ] A versioned, separate, curated evaluation set and an evaluation report with actual measurements.
- [ ] Clickable/traceable citations in the UI and a tested insufficient-evidence response.
- [ ] Job-fit evidence output that explains support, missing evidence, and uncertainty without making hiring decisions.
- [ ] Automated unit, integration, API, and safety tests in CI.
- [ ] API docs, health check, structured logs, error handling, and clear configuration.
- [ ] Deployed website with secrets managed by the hosting environment and persistent storage configured correctly.
- [ ] Screenshots or a short demo video using only fictional records.
- [ ] A limitations / responsible-AI section and a short explanation of what you would improve next.

A strong resume bullet should include only results you actually measured. For example: “Built a citation-grounded recruiting RAG copilot with hybrid retrieval and cross-encoder reranking; evaluated retrieval, source attribution, abstention and latency on a curated synthetic benchmark.” Replace this with actual measured metrics after running the project; do not invent percentages.

## 13. Reference links

- O*NET current releases and database license: <https://www.onetcenter.org/db_releases.html>
- ESCO dataset download and formats: <https://esco.ec.europa.eu/en/use-esco/download>
- Optional synthetic candidate/job matching dataset card: <https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic>
- NIST AI Risk Management Framework: <https://www.nist.gov/itl/ai-risk-management-framework>

Dataset metadata and hosted services can change. Recheck the source page and license before each use or redistribution.
