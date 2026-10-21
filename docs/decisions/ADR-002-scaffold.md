# ADR-002: Repository scaffold choices

Status: Proposed (Stage 01)
Date: 2026-10-21

## Decisions

| Topic | Choice | Reason | Alternative |
|---|---|---|---|
| Project file | `pyproject.toml` with setuptools | One standard file for metadata, dependencies and tool settings | `requirements.txt` only, or Poetry/uv |
| Package layout | `backend/app/`, installed with `pip install -e .` | Matches the README layout | Flat layout |
| Python version | 3.11 to 3.13, tested on 3.12 | Widely available, and supported by the main libraries | Latest release only |
| Version pins | Lower and upper bounds in `pyproject.toml`, exact versions saved with `pip freeze` after install | The sandbox for Stage 01 had no network, and the version sources I could search disagreed, so exact current versions were not confirmed | Exact pins written from memory |
| Lint and format | ruff only | One tool for both jobs | black plus flake8 plus isort |
| Settings | `pydantic-settings` | Typed fields, clear errors on bad values, `SecretStr` for keys | Plain `os.environ` |
| Logging | Standard library `logging` with a small JSON formatter | No extra package. Blocks text fields by name | structlog |
| Commands | Plain commands in the README | Works the same on Windows, macOS and Linux | Makefile |
| CORS | Not enabled | A wildcard default is unsafe. The origin setting exists for Stage 13 | Add middleware now |
| Docker | `api` service only | Qdrant and PostgreSQL are not used yet | Full compose file with unused services |

## Limits

- The log field filter works on field names. It does not scan values, so a developer who puts document text in a field called `note` would leak it. Code review and the Stage 12 log test cover this.
- `/health` only says the process is running. It does not check Qdrant or a database. Those checks are added with those services.
- The Dockerfile was not built during Stage 01.
