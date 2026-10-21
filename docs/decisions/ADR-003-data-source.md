# ADR-003: Data source plan for the first release

Status: Proposed (Stage 02)
Date: 2026-10-21

## Context

The project needs documents to search, and test questions with known answers. The README lists four options. This record compares them, using the source pages as they were on 2026-10-21, and picks the smallest path that lets us finish the pipeline and measure it honestly. Nothing has been downloaded.

## Options

### 1. Fictional starter corpus (we create it)

| Item | Detail |
|---|---|
| What it gives | Full prose for resumes, job descriptions and assessment notes. We control the edge cases: conflicts, vague wording, planted injection text, fake contact details. |
| Limits | We write it, so it may be simpler than real documents. Text can sound templated if the generator is lazy. |
| License | None to check. Each record is labelled `synthetic-original`. |
| Size | Small. My estimate is a few hundred KB of text. Measured in Stage 03. |
| Effort | Medium. A seeded generator for the bulk, plus about 13 hand-written edge-case records. |

### 2. ESCO

| Item | Detail |
|---|---|
| What it gives | Occupation and skill labels with descriptions, in 28 languages. |
| Facts checked | The download page lists v1.2.1 (last update 10 December 2025). Download is free. Formats include CSV, ODS, RDF, TTL, XML and JSON-LD. You accept a privacy statement and receive the link by email. |
| Limits | A vocabulary, not documents. European framing. Skill labels are not evidence in a resume. |
| License | Not read on the download page. The terms must be read before use. |
| Size | Not checked. Filters let you download one language and one content type. |
| Effort | Low to medium, plus the email step. |

### 3. O*NET

| Item | Detail |
|---|---|
| What it gives | Occupation data and skill-related tables for the U.S. labor market. |
| Facts checked | The releases page lists 31.0 (August 2026) as the current production release. The page states that all versions are under Creative Commons Attribution 4.0. Formats include Excel, CSV, JSON, text, SQL and RDF. |
| Limits | A vocabulary, not documents. U.S. framing. Which table holds the skill terms we want must be checked in its data dictionary. |
| License | CC BY 4.0, so an attribution notice is required wherever the data is redistributed. |
| Size | Not checked. |
| Effort | Low to medium. |

### 4. Hugging Face candidate-matching-synthetic

| Item | Detail |
|---|---|
| Declared | Synthetic. MIT license on the page header and in the card. 10,000 resumes, 2,500 jobs, 2,500 match records (30 relevant resumes per job, about 75,000 pairs). English. 104 MB in total. Generated with Qwen2.5-0.5B-Instruct. |
| Labels | A resume counts as relevant to a job when at least 60% of the job's must-have skills appear in the resume. This is a skill overlap rule. |
| What I saw | The viewer showed the first 100 resumes. Every one has the same three experience bullets. The summary is one templated sentence ("Role with N years of experience in Industry", including "1 years"). The only varied content is the skill list, the role and a few categories. There are 73 distinct skills in total. |
| Card and viewer differ | The card says all data is in a `train` split. The viewer shows one subset named `default` with a split named `resumes`. This must be checked at download time. |
| Limits | There is almost no prose to retrieve or cite, so it cannot test grounded answers or citation correctness. The card's own Recall@K table is computed with its own overlap rule, so it is circular. The card claims "production ready" quality, which I did not verify. |
| Effort | Medium. Needs a loader, a clean split by resume and job, and a manual review sample. |

## Decision

1. Stage 03 generates the fictional corpus described in `docs/corpus-plan.md`: 50 candidate profiles, 15 job descriptions, 60 assessment records.
2. No external taxonomy is needed for the first release. The structured skill field in the fictional corpus is enough for exact skill search and job-fit.
3. If a taxonomy is added later (not before Stage 06 results are in), it will be O*NET, used only as a skill vocabulary, with attribution. Reasons: English only (assumption A-02), simple tabular downloads, license already visible. ESCO is not added. ESCO and O*NET will not be mixed, so no crosswalk is needed.
4. The Hugging Face dataset is not used in the first release. It may be used later as a structured-only test of skill overlap and scale, never as proof of hiring suitability. If it is used, the holdout is split by resume ID and job ID, a sample is reviewed by hand, and the license and schema are checked again on the download date.

## Why this is the smallest effective path

The core claims of the project are grounded answers, correct citations, safe refusals and honest job-fit wording. These need prose and controlled edge cases. Only our own corpus gives both. A taxonomy adds vocabulary but no evidence text, and the HF data adds scale but no prose.

## Consequences

- We carry the risk that our own text is too clean or too repetitive. Stage 03 reports the share of repeated sentences across profiles and the edge-case count, so the weakness is visible.
- Results on a 50-profile corpus show whether the pipeline works. They do not show how it behaves on real resumes. The README and dataset card say this.
- The golden set is written before the corpus exists. Cases that depend on the corpus are marked `draft` and state what the corpus must contain. Stage 03 builds the corpus to satisfy them and then marks them `bound`.

## Review triggers

- Stage 06 shows no difference between dense and hybrid search because the corpus is too easy. Then a larger or harder source is reconsidered.
- A license on a source page changes before download.
- The generator output looks templated enough to make retrieval trivial.
