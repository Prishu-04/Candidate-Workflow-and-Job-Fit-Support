# Risk register

Likelihood and impact are first guesses (L, M, H) made at Stage 00 before any measurement. They are reviewed at Stages 07, 10 and 12. "Residual risk" is what is left after the planned controls. None of these controls make the system compliant or unbiased.

| ID | Risk | Cause | L | I | Planned controls | Residual risk | Stage | Evidence of control |
|---|---|---|---|---|---|---|---|---|
| R-01 | Hallucination or wrong citation | LLM adds claims not in the chunks, or cites the wrong chunk | M | H | Answer only from retrieved chunks. Validator checks IDs and schema. Groundedness and citation metrics. Abstention path | Subtle unsupported claims can still pass the validator | 07, 09 | Citation tests, evaluation report |
| R-02 | Prompt injection in documents | A resume or job text contains instructions | M | H | Documents handled as data. Delimited prompt section. Output validation. Planted-injection tests | New attack wording may still work | 07, 10 | Injection test set |
| R-03 | PII exposure | Real or planted PII in documents, logs, prompts or index | M | H | Synthetic data only. Redaction at ingestion. No full text in logs. Git-ignored raw data | Redaction patterns miss unusual formats | 04, 10, 12 | PII fixture test, log test |
| R-04 | Unauthorized access | Caller changes an ID, or filter applied after search | M | H | Scope filter inside the query. Access layer. Authorization tests with swapped IDs | Demo auth is simple and not a full identity system | 05, 10, 11 | Scope tests |
| R-05 | Dataset leakage | Golden cases indexed in the corpus, or held-out cases used for tuning, or paired resume and job in both splits | M | M | Separate folders. Build check. Holdout rule. Split by candidate and job | Informal tuning on the holdout is hard to detect | 02, 09 | Build check, split report |
| R-06 | Biased job-fit assumptions | Skill taxonomy gaps, proxy words, uneven resume style, synthetic labels from simple skill overlap | M | H | No protected-trait or personality inference. "Not found in supplied evidence" wording. Human review notice. No score or ranking. Label caveats in the data card | Writing style and vocabulary can still shape which evidence is found | 02, 08, 10 | Wording tests, bias notes in evaluation report |
| R-07 | Third-party provider exposure | Prompts and chunks go to the LLM provider | M | M for synthetic data, H for real data | Synthetic only in demo. Provider terms checked before any real data. Provider configurable | Provider outages and policy changes | 07, 10 | Provider review note |
| R-08 | Cost growth | Long prompts, many evaluation runs, LLM-based judging | M | M | Record tokens per request. Cap context size. Cache embeddings. Report cost per run | Price changes outside the project | 09, 12 | Cost section of report |
| R-09 | Latency | Cross-encoder on CPU, large context, provider delay | H | M | Small rerank pool. Measure p50 and p95 per stage. Fallback to fused ranking | Free hosts may stay slow | 06, 12 | Latency report |
| R-10 | Persistence loss or drift | Index or database not on a persistent volume. Index built with old settings | M | M | Index manifest with settings. Rebuild script. Persistent volume in deployment | Manual deployment mistakes | 05, 12, 13 | Restart test, manifest check |
| R-11 | Synthetic labels treated as truth | Rule-based match labels used as ground truth | M | M | Separate manually reviewed test set. Data card states the label method | Reviewer error in the small manual set | 02, 03 | Data card |
| R-12 | Over-reliance on output | User reads "supported" as "suitable" | M | H | Review notice on every job-fit output. No overall score. Plain wording. UI shows source text next to each status | Users may still skip the sources | 08, 13 | UI checklist |
| R-13 | Unreliable abstention threshold | Reranker scores are not calibrated and vary with the corpus | M | M | Pick threshold from evaluation data. Store as a setting. Report abstention quality | Threshold may not hold on new data | 07, 09 | Abstention metrics |
| R-14 | Secret leakage | Keys in code, logs, notebooks or the client | L | H | Environment variables. `.env` ignored. `.env.example` has placeholders. Secret scan in CI | Human error | 01, 12 | CI scan |
| R-15 | License or terms issue in datasets | Dataset license differs from the card, or attribution missing | L | M | Check license at Stage 02 and again at Stage 03. Manifest lists license and source | Terms may change later | 02, 03 | Data manifest |
| R-16 | Stale or conflicting evidence | Two documents disagree, or an old record is out of date | M | M | Keep dates in metadata. Show both sources. Mark as needs human review | Dates may be missing | 04, 08 | Conflict test cases |

## Review rule

At the end of each stage, check whether any risk changed, whether a control now has a test, and whether a new risk appeared. Update this file in the same commit as the stage work.
