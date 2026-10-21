# Evaluation design

This document explains how the golden set in `evals/golden_set.jsonl` is built, split and used. No baseline results exist yet.

## 1. What the golden set is

A list of test questions, one JSON object per line. Each case has a stable ID (`EV-0001` and up), a category, a split (`dev` or `holdout`), the expected behavior (`answer`, `abstain` or `refuse`), the documents that should be found, the claims the answer should make, the citations it must carry, and claims it must not make. The schema is `EvaluationCase` in `backend/app/data/schemas.py`.

## 2. Case status

| Status | Meaning |
|---|---|
| draft | The corpus does not exist yet. The case states what the corpus must contain (`corpus_requirements`). |
| bound | Stage 03 checked the document IDs against the real corpus and filled in claims and citations. |
| reviewed | A person read the case and the matching documents and agreed the label is right. |

All 36 starter cases are `draft`. Chunk IDs (`relevant_chunk_ids`) stay empty until Stage 04 creates chunks.

## 3. Categories and planned size

| Category | What it tests | Starter | Planned |
|---|---|---|---|
| exact_skill | Finding a named skill | 4 | 8 |
| paraphrase | Finding the same idea in other words | 3 | 8 |
| multi_document | Using a job, a resume and an assessment together | 3 | 8 |
| missing_evidence | Saying "not found" when the topic is absent | 3 | 7 |
| ambiguous_evidence | Showing uncertainty on vague text | 3 | 6 |
| conflicting_records | Reporting a disagreement between sources | 3 | 6 |
| prompt_injection | Ignoring instructions inside documents or questions | 4 | 8 |
| unauthorized_access | Refusing records outside the caller's scope | 3 | 6 |
| pii_request | Refusing contact details | 3 | 6 |
| protected_trait | Refusing age, gender or personality guesses | 2 | 4 |
| hiring_decision | Refusing hire or reject advice and ranking | 2 | 4 |
| job_fit | Per-requirement statuses with citations | 3 | 9 |
| Total | | 36 | 80 |

## 4. Split rules

- The split is written into each case when it is created and is not changed afterwards.
- Every category has at least one `dev` and one `holdout` case. A test checks this.
- About one third of cases are `holdout`. A test checks that the share stays between 20% and 40%.
- Cases about the same candidate, job or edge-case record are kept in the same split when possible, so a tuning change that fixes one case does not quietly fix its holdout twin.

## 5. Preventing data leakage

1. Eval files live in `evals/`. Corpus files live in `data/`. The Stage 04 index build fails if any path under `evals/` is passed to ingestion.
2. Questions, expected claims and forbidden claims are never added to prompts, chunk text or the index.
3. Prompts and settings are tuned on `dev` cases only.
4. If a failure on `holdout` is investigated, the case is moved out of the holdout set and a replacement is written. The move is recorded in the change log below.
5. Corpus records are written to satisfy the cases (for example `cand-046` holds an injection line). That is test-fixture design, not leakage, but it means the corpus is easy for those cases. The report must say so.

## 6. Preventing metric cherry-picking

1. The metric list is fixed before the first baseline: Recall@K, MRR, answer correctness, groundedness, citation correctness, abstention quality, refusal quality, job-fit status accuracy and F1, latency (p50, p95) and cost per request.
2. K values are set once (K = 5 and K = 10) and reported together.
3. Every evaluation run writes a report that includes the golden set hash, corpus manifest version, model names, prompt version and settings. Reports are kept, including bad ones.
4. Holdout runs happen only at stage gates (end of Stages 06, 07, 08 and before release). Each run is logged with a date and reason. The number of holdout runs is reported with the final scores.
5. Targets such as "Recall@5 of at least 0.80" are written down before the baseline is measured. They are goals, not claims.
6. A case is removed only with a written reason in the change log. Removing cases because the system fails them is not allowed.

## 7. Limits

- Labels are written by one person. Ambiguous and conflicting cases involve judgment, so a second reader should review them (status `reviewed`).
- 80 cases over 12 categories gives few cases per category. Small differences between systems will not be meaningful. Reports show counts next to percentages.
- Job-fit labels come from a rule plus review. They are not hiring truth.

## 8. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-10-21 | Created 36 draft cases (24 dev, 12 holdout) | Stage 02 |
