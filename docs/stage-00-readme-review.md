# Stage 00 README review

This note lists problems found in the README and the project card, the default taken for each, and the stage that settles it. Nothing in the README was edited.

## 1. Contradictions and gaps

| # | Finding | Why it matters | Default taken | Settled in |
|---|---|---|---|---|
| 1 | The diagram connects job-fit only to canonical records, but the text says job-fit shares retrieval. | Without retrieval, job-fit has no way to find evidence in a long profile. | Job-fit reads requirements from the job record and gets evidence through scoped retrieval (architecture.md 2.1). | Needs your approval, then README edit |
| 2 | The project card lists "Accuracy/F1". The README metrics table has no classification metric. | F1 only makes sense for a labelled task. | Use job-fit status (supported, not found, needs review) as the labelled task, scored on a manually reviewed set. | Stage 02, 09 |
| 3 | The project card suggests "LangChain/LlamaIndex" and "Chroma/Qdrant". The README picks LangChain (selectively) and Qdrant. | Two stacks would double the work. | Follow the README. ADR-001 lists the others as alternatives. | ADR-001 |
| 4 | The card's advanced extension mentions streaming or scheduled updates. The README has feedback, monitoring and cost but not streaming. | Possible scope gap. | Streaming is not required. It is listed as an optional later extension only. | After Stage 13 |
| 5 | The BM25 library is not named. | BM25 can come from a Python package, or from Qdrant sparse vectors. | Decide at Stage 06 and compare setup cost. | Stage 06 |
| 6 | PostgreSQL is "optional until needed", but feedback, audit records and "persistent storage" are required. | Unclear when it enters. | Add at Stage 12 only if feedback and audit records need a database. Earlier stages use files. | Stage 12 |
| 7 | Ingestion redacts PII, but recruiters want to ask about named candidates. | Redacting names could break queries. | Use stable pseudonymous IDs as the main handle. Names are fictional. Redaction targets contact details and ID numbers. | Stage 02, 04 |
| 8 | Access control sits in the diagram but the security stage is 10. | Scope filters need metadata at Stage 04 and filtered search at Stage 05. | Build scope metadata and filtered search early. Stage 10 adds the access layer and tests. | Stage 04, 05, 10 |
| 9 | "Enough relevant evidence?" has no definition. | Reranker scores are not calibrated, so a fixed number may not carry over. | Threshold is a setting chosen from evaluation data. | Stage 07, 09 |
| 10 | A recruiter question like "who mentions Python" returns several candidates, which looks like ranking. | Ranking candidates as a fit decision is out of scope. | Search results are ranked by relevance to the question only. The interface says so. | Stage 07, 13 |
| 11 | The README says O*NET release 31.0 is current (August 2026) and quotes a Hugging Face license. | I could not check these during Stage 00. Pages and licenses change. | Treat them as unverified. Recheck both at Stage 02. | Stage 02 |
| 12 | The deployed demo needs local models and Qdrant. Free hosts may not have enough memory. | Stage 13 could fail late. | Measure memory and latency in Stage 12. Streamlit or a hosted embedding API are fallbacks. | Stage 12 |

## 2. Parts that may be too complex

- Hybrid search, a reranker, LLM-based groundedness scoring, PostgreSQL, Docker Compose and Next.js are all in one project. The staging already lets each part be added and measured in turn, so the plan is to keep them but to finish a simple working version first: dense retrieval, citations, abstention.
- Optional taxonomies (ESCO, O*NET) and the larger synthetic dataset are not needed for a first version. The README already says to add at most one taxonomy after the core pipeline works.
- If time is short, the first things to drop are PostgreSQL and the Next.js frontend (replace with a simpler interface). Retrieval, citations, abstention and evaluation are the core of the portfolio value.

## 3. Risky assumptions

- That synthetic match labels are correct. They come from skill overlap rules.
- That a reranker improves results on a small corpus. It may not. It is measured.
- That a small corpus of about 50 profiles is enough to show differences between retrieval methods. Differences may be too small to see, and the report should say so if that happens.
- That a public LLM provider is acceptable for the demo. This holds only for synthetic data.

## 4. Stage sequence check

The README stage table runs 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13 and ends with the full-stack deployment stage. requirements.md section 8 repeats it in the same order, with Stage 13 last. I could only check the table, because the prompt files for stages 01 to 13 were not provided. When you run each stage, compare its prompt file with the table.

## 5. Open questions

These have defaults, so none blocks Stage 01. Please confirm or change them.

1. Approve the README diagram change from finding 1?
2. Is English-only acceptable for the first version?
3. Is a simple API key or role token enough for the demo access control?
4. Should Streamlit stay as an allowed fallback if Stage 13 time runs short?
