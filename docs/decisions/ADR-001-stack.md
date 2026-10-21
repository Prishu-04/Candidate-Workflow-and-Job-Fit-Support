# ADR-001: Technology stack

Status: Proposed (Stage 00)
Date: 2026-10-21

## Context

The project is a portfolio RAG application over fictional recruiting data. It must be small enough for one learner to build in stages, testable offline, easy to explain, and able to run locally and then be deployed. Package versions, model names and hosting limits change often, so this record names categories and defaults. Exact versions are pinned in Stage 01 after checking current documentation.

## Decision

| Layer | Choice |
|---|---|
| Language | Python |
| Backend | FastAPI with Pydantic |
| Vector database | Qdrant |
| Keyword search | BM25 |
| Rank fusion | Reciprocal rank fusion (RRF) |
| Reranker | Sentence Transformers cross-encoder |
| Embeddings | Sentence Transformers, local |
| LLM | Hosted provider behind a configuration interface |
| RAG helper library | LangChain, used only for narrow parts |
| Frontend | Next.js with TypeScript, built in Stage 13 |
| Tests | pytest |

## Reasons and alternatives

### Python

Most NLP and retrieval libraries are Python first. The evaluation code, ingestion and API can share one language and one test tool.
Alternative: TypeScript for everything. This would simplify the frontend link but has fewer retrieval and evaluation tools.

### FastAPI with Pydantic

Request and response types are checked automatically and OpenAPI docs are generated. The same Pydantic models can describe the data contracts, which supports the schema requirements.
Alternatives: Flask (less built-in validation), Django (more than this project needs).

### Qdrant

It stores vectors with metadata payloads and supports filtered search, which the scope rule (FR-10) needs. It runs locally in Docker and also has a hosted option, so the local-to-deployed path is short.
Alternatives:
- Chroma: simpler to start and the project card lists it. Metadata filtering and the hosted path are less clear for this use. It is a reasonable swap if Qdrant setup becomes a blocker.
- pgvector: one database for everything, but hybrid search and tuning need more manual work.
- FAISS: fast, but it is a library, not a database. Persistence and filters would be built by hand.

### BM25 plus RRF

Dense search can miss exact terms such as "PyTorch" or "AWS". BM25 matches the words directly. The raw scores of the two methods are on different scales, so RRF merges by rank position and avoids score tuning.
Alternatives:
- Dense only: simpler. It stays as the baseline that hybrid has to beat, measured in Stage 06.
- Weighted score blending: needs normalization and tuning.
- Qdrant's own sparse vectors: possible and may reduce the number of systems. The BM25 library choice is deferred to Stage 06.

### Cross-encoder reranker

A cross-encoder reads the query and one chunk together, which usually ranks closer pairs better than comparing separate vectors. It is slow, so it only runs on a small pool from the fused list.
Alternatives: no reranker (faster, lower precision), LLM-based reranking (higher cost and latency, harder to test). Whether the reranker helps is measured in Stage 06. If it does not help on this data, the report says so.

### Local embeddings

No per-call fee, repeatable results, and no document text leaves the machine at embedding time.
Alternative: hosted embedding API. Easier on small hosts, but adds cost and sends text to a third party. The embedding provider sits behind an interface so it can be swapped.

### Configurable LLM provider

Providers, prices and model names change. The provider module hides these behind one interface, and tests use a fake provider.
Alternative: lock to one provider. Faster to build, harder to compare or replace.

### LangChain, used narrowly

Useful for text splitters and some integrations. The core retrieval, citation and job-fit logic is written explicitly so it can be read and tested.
Alternatives: LlamaIndex (similar role, more opinionated pipeline), no framework (most control, more code to write). Any LangChain use must stay behind our own interfaces.

### Next.js

React with TypeScript is common in job listings and has good deployment options. It is built last, on a tested API.
Alternatives: Streamlit or Gradio (much faster to build, less like a real product interface). A fallback if Stage 13 time runs short.

## Consequences

- More moving parts than a single-script demo: Qdrant, two Sentence Transformers models, an LLM provider.
- CPU latency and memory of the cross-encoder and embeddings need measuring before deployment.
- The first working version should be the smallest path: dense retrieval, citations, abstention. Hybrid, reranking and job-fit are added by stage and each one is compared against the previous step.
- PostgreSQL is not part of the first versions. It enters only if feedback and audit records need it.

## Review triggers

Revisit this decision if any of these happen:

- Qdrant cannot be run reliably on the learner's machine or the chosen host.
- Local models do not fit in deployment memory.
- Hybrid or reranking shows no gain on the evaluation set.
- A package or model in the stack is deprecated or its license changes.
