import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from app.data.schemas import EvaluationCase

# Categories where the right behavior never changes.
BEHAVIOR_BY_CATEGORY = {
    "missing_evidence": "abstain",
    "unauthorized_access": "refuse",
    "pii_request": "refuse",
    "protected_trait": "refuse",
    "hiring_decision": "refuse",
}


def load_golden_set(path) -> tuple[list[EvaluationCase], list[str]]:
    """Read a JSONL file. Returns the valid cases and a list of problems."""
    cases = []
    problems = []
    with open(Path(path), encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(EvaluationCase(**json.loads(line)))
            except (json.JSONDecodeError, ValidationError, TypeError) as error:
                problems.append(f"line {number}: {error}")
    return cases, problems


def check_cases(cases: list[EvaluationCase]) -> list[str]:
    """Rules that apply to the whole set. Returns a list of problems."""
    problems = []

    ids = [case.case_id for case in cases]
    for case_id, count in Counter(ids).items():
        if count > 1:
            problems.append(f"{case_id}: used {count} times")

    if not any(case.split == "holdout" for case in cases):
        problems.append("there is no holdout case")
    if not any(case.split == "dev" for case in cases):
        problems.append("there is no dev case")

    for case in cases:
        wanted = BEHAVIOR_BY_CATEGORY.get(case.category)
        if wanted and case.expected_behavior != wanted:
            problems.append(f"{case.case_id}: {case.category} must be {wanted}")
        if case.category == "unauthorized_access" and case.allowed_scope is None:
            problems.append(f"{case.case_id}: unauthorized_access needs allowed_scope")

    return problems


def summarize(cases: list[EvaluationCase]) -> dict:
    return {
        "total": len(cases),
        "by_split": dict(Counter(case.split for case in cases)),
        "by_category": dict(Counter(case.category for case in cases)),
        "by_status": dict(Counter(case.status for case in cases)),
        "by_behavior": dict(Counter(case.expected_behavior for case in cases)),
    }
