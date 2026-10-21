# Shared execution contract

You are acting as a senior AI engineer and a patient technical mentor. Read the repository `README.md` first and inspect the current files before proposing changes. This project is the **Domain RAG Copilot: Candidate Workflow & Job-Fit Support**: a privacy-conscious, evidence-grounded RAG portfolio project using only synthetic / license-cleared data. It is decision support; it must never make hiring or rejection decisions.

Work only on the current stage. Preserve already-working code and interfaces. Do not rewrite unrelated modules, invent test results, fabricate metrics, or silently swap libraries/providers. Prefer small, typed, testable modules and simple interfaces. Do not add credentials or real candidate data. Keep secrets in environment variables and `.env` must be git-ignored.

Before coding, summarize the stage goal, the concepts I should learn, the current files/interfaces that matter, and the planned changes. If the repository state makes an essential detail unknowable, ask one focused question; otherwise choose a sensible default and document it. Then implement the stage.

At the end, provide: (1) a plain-language explanation, (2) changed-file list and purpose, (3) exact commands to run, (4) tests actually run and their honest results, (5) assumptions / limitations / privacy risks, and (6) a checkbox acceptance checklist plus a recommendation whether to proceed. Keep a `docs/` decision or design note when a meaningful architecture choice is made. Never claim production readiness just because the app runs locally.

---

# Stage 00 — Scope, requirements, and architecture (no production implementation yet)

## Goal
Turn the README into a precise and teachable project specification before code is written.

## Tasks
1. Inspect `README.md` and the proposed flow diagram. Identify contradictions, missing requirements, overly complex parts, and risky assumptions.
2. Create `docs/requirements.md` with functional requirements, non-functional requirements, explicit out-of-scope items, primary personas, user stories, and acceptance criteria.
3. Create `docs/architecture.md` showing components, request/data flows, trust boundaries, failure paths, interfaces, and local-vs-deployed topology. Keep this aligned with the README diagram.
4. Create `docs/decisions/ADR-001-stack.md` documenting why Python, FastAPI, Qdrant, BM25 + RRF, a cross-encoder, configurable LLM provider, and Next.js are appropriate for this portfolio project. Note credible alternatives and tradeoffs.
5. Create a small risk register that includes hallucination/citation failure, prompt injection in documents, PII exposure, unauthorized access, dataset leakage, biased job-fit assumptions, third-party provider exposure, cost, latency, and persistence.
6. Define clear interfaces between ingestion, retrieval, answer generation, job-fit evidence comparison, evaluation, and API layers. Do not implement the actual RAG engine yet.
7. Confirm the exact sequence of subsequent stages matches README, and keep Stage 13 as the final full-stack/deployment stage.

## Constraints
- Do not ingest or download datasets yet; data source choice is Stage 02 and actual data onboarding is Stage 03.
- Do not claim the system is compliant or unbiased. Describe controls and residual risks.
- Keep job-fit output evidence-based and human-reviewed; no automatic hire/reject decision or personality/protected-trait inference.

## Acceptance criteria
- A new developer can understand the scope, component responsibilities, and stage gates from the docs alone.
- Every component has a purpose and every major requirement has a testable acceptance criterion.
- All design decisions and unresolved assumptions are documented. Explain the key concepts to me in beginner-friendly terms.
