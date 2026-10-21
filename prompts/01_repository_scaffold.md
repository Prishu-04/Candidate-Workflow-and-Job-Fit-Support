# Shared execution contract

You are acting as a senior AI engineer and a patient technical mentor. Read the repository `README.md` first and inspect the current files before proposing changes. This project is the **Domain RAG Copilot: Candidate Workflow & Job-Fit Support**: a privacy-conscious, evidence-grounded RAG portfolio project using only synthetic / license-cleared data. It is decision support; it must never make hiring or rejection decisions.

Work only on the current stage. Preserve already-working code and interfaces. Do not rewrite unrelated modules, invent test results, fabricate metrics, or silently swap libraries/providers. Prefer small, typed, testable modules and simple interfaces. Do not add credentials or real candidate data. Keep secrets in environment variables and `.env` must be git-ignored.

Before coding, summarize the stage goal, the concepts I should learn, the current files/interfaces that matter, and the planned changes. If the repository state makes an essential detail unknowable, ask one focused question; otherwise choose a sensible default and document it. Then implement the stage.

At the end, provide: (1) a plain-language explanation, (2) changed-file list and purpose, (3) exact commands to run, (4) tests actually run and their honest results, (5) assumptions / limitations / privacy risks, and (6) a checkbox acceptance checklist plus a recommendation whether to proceed. Keep a `docs/` decision or design note when a meaningful architecture choice is made. Never claim production readiness just because the app runs locally.

---

# Stage 01 — Repository scaffold and developer workflow

## Goal
Build a small, repeatable engineering foundation without implementing the RAG functionality prematurely.

## Tasks
1. Set up Python project/dependency management using `pyproject.toml`; choose and pin compatible versions based on current official package docs. Prefer a supported, widely available Python version and document it.
2. Create the initial `backend/app/` package and minimal FastAPI entrypoint with `/health` only. Add typed configuration/settings validation.
3. Add structured logging that avoids logging full document contents, `.env.example` with placeholders only, and `.gitignore` covering virtual environments, caches, raw/processed data, local databases/indexes, secrets, and build artifacts.
4. Configure formatting/linting and pytest. Add a trivial unit test plus an API health test. Set up a `Makefile` or equivalent cross-platform documented commands if helpful.
5. Add an initial Dockerfile / Compose scaffold where appropriate, but do not pretend all services are ready yet. Keep the environment simple and explain which services are actually used.
6. Add a brief developer setup section to README without deleting existing project information.

## Constraints
- No dataset download, vector index, frontend, LLM call, or candidate comparison logic yet.
- Secrets must never have real values in source files. Do not configure CORS broadly as a production default; document the future origin setting.
- Avoid installing overlapping frameworks for the same task.

## Acceptance criteria
- A clean checkout can be installed using documented commands.
- `pytest`, lint/format check, and the health endpoint work; include exact commands and real results.
- App settings fail clearly for invalid configuration. `.env` is ignored by Git.
