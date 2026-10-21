# Data governance

These rules apply to every file added to the repository.

## 1. Principles

- Only fictional or license-cleared data is used. No real candidate, employee or applicant data is committed, uploaded or sent to a model provider.
- Every record has a source, a license label and a version.
- Anything that cannot be explained by the manifest does not belong in the repository.

## 2. Consent and provenance

| Question | Rule |
|---|---|
| Whose data is it? | Fictional records are ours. External datasets are used only under their published license. |
| Is consent needed? | Not for fictional data. For any real data, written permission from each person is required first, and that data stays out of the public repository and the public demo. |
| How is origin shown? | Each record carries a `DocumentSource` with source name, version, license, `is_synthetic`, classification, date and checksum. |
| What proves it? | A manifest in `data/manifests/` lists every file with its checksum. |

## 3. Licensing and attribution

| Source | License as checked on 2026-10-21 | Action |
|---|---|---|
| Our fictional corpus | `synthetic-original` | Say so in the README and dataset card |
| O*NET 31.0 (if used later) | Creative Commons Attribution 4.0, per the releases page | Add the attribution notice wherever the data or derived lists appear |
| ESCO v1.2.1 (not planned) | Terms not read yet | Read the terms before any use |
| Hugging Face candidate-matching-synthetic (not planned) | MIT per the page and card | Recheck on download day. Keep the license text with the files |

The license check is repeated in Stage 03 before any download.

## 4. Data classification

| Class | Meaning | Can be committed |
|---|---|---|
| synthetic_public | Fictional and safe to publish | Yes |
| licensed_public | Public data under a license that allows redistribution | Yes, with attribution |
| restricted | Anything else | No |

The schema rejects a record marked `synthetic_public` that is not marked synthetic.

## 5. PII and redaction

- No name, address, age, gender or photo field exists in the schemas.
- The only record with contact-style details is `cand-045`, made from reserved example values (example.com, 555-01xx). It exists to test redaction.
- Ingestion (Stage 04) redacts email, phone and ID-number patterns. Tests check that planted values never reach chunks, the index or logs.
- Redaction patterns will miss some formats. This is a known limit.

## 6. Retention and deletion

- Fictional data stays in Git history.
- Local indexes, caches and logs are not committed and can be deleted at any time. They are rebuilt from the manifest.
- If anything real is found in the repository, stop, remove it from the working tree and from Git history, rotate any exposed secrets, and record the incident in the risk register.

## 7. Git handling

| Path | Tracked |
|---|---|
| `data/samples/`, `data/manifests/` | Yes |
| `data/raw/`, `data/processed/` | No |
| Vector store folders, local databases | No |
| `evals/golden_set.jsonl` | Yes |
| `.env` | No. Only `.env.example` with placeholders is tracked |

## 8. Source manifest fields

File path, document ID, doc type, source name, source version, license, `is_synthetic`, classification, created date, SHA-256 checksum, generator seed (if generated), notes.

## 9. Evaluation data

The golden set is kept apart from the corpus and is never indexed. See `docs/evaluation-design.md` for the split and leakage rules.

## 10. Third-party providers

Prompts sent to a hosted model contain document text. Only fictional data is allowed in that path. Before any other data is used, the provider's data-use terms must be read and the decision recorded in an ADR.

## 11. Checklist before adding data

- [ ] Source and license written down and checked today
- [ ] Records pass the schemas
- [ ] No real names or contact details (except the planted test record)
- [ ] Manifest and checksums updated
- [ ] Dataset card updated
- [ ] Nothing from `evals/` is in a corpus folder
