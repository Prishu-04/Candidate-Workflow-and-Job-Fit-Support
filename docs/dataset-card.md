# Dataset card (template)

Fill this in during Stage 03 and update it with every corpus version. Delete the guidance in brackets once a section is filled.

## 1. Summary

- Name: [fictional candidate workflow corpus]
- Version: [x.y]
- Date: [YYYY-MM-DD]
- Owner: [name or handle]
- Purpose: [what the dataset is used for, and what it is not used for]

## 2. Source and license

| Item | Value |
|---|---|
| How the data was created | [seeded generator, hand-written, other] |
| Generator script and seed | [path, seed value] |
| License of each file group | [synthetic-original, CC-BY-4.0, MIT, other] |
| Attribution text required | [text, or "none"] |
| Date the license was checked | [YYYY-MM-DD] |

## 3. Contents

| Type | Count | ID range | Notes |
|---|---|---|---|
| Candidate profiles | [ ] | [ ] | |
| Job descriptions | [ ] | [ ] | |
| Assessment records | [ ] | [ ] | |

Fields per record type: [link to `backend/app/data/schemas.py`].
Sentence variants per section: [counts].
Share of sentences repeated across profiles: [measured value].

## 4. Personal data

- Real people: [none]
- Names in records: [none]
- Planted fake contact details: [which record, which reserved values]
- Review done before commit: [who, when, how]

## 5. Known limits

- [Text written by one author and may be simpler than real resumes.]
- [Skill lists are short and drawn from a fixed pool.]
- [Match labels are rule-based plus review, not hiring truth.]
- [Languages covered.]

## 6. Bias and fairness notes

- [Which attributes are excluded from the schema, and why.]
- [Vocabulary or style that could favor some writing styles over others.]
- [What was not tested.]

## 7. Intended and out-of-scope use

- Intended: [testing retrieval, citations, refusals and job-fit wording on fictional data]
- Not intended: [real hiring decisions, training a ranking model, claims about real populations]

## 8. Integrity

- Manifest: [path]
- Checksums: [where they are stored]
- Rebuild command: [command]
- Change history: [table of versions]
