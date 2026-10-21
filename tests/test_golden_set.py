import json
from pathlib import Path

from app.data.golden import check_cases, load_golden_set
from app.data.schemas import EvaluationCase

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "evals" / "golden_set.jsonl"


def test_golden_set_file_is_valid():
    cases, problems = load_golden_set(GOLDEN_PATH)
    assert problems == []
    assert check_cases(cases) == []


def test_golden_set_has_enough_cases():
    cases, _ = load_golden_set(GOLDEN_PATH)
    assert len(cases) >= 30


def test_every_category_has_dev_and_holdout_cases():
    cases, _ = load_golden_set(GOLDEN_PATH)
    categories = set(EvaluationCase.model_fields["category"].annotation.__args__)
    for category in categories:
        splits = {case.split for case in cases if case.category == category}
        assert splits == {"dev", "holdout"}, category


def test_holdout_share_is_reasonable():
    cases, _ = load_golden_set(GOLDEN_PATH)
    holdout = [case for case in cases if case.split == "holdout"]
    share = len(holdout) / len(cases)
    assert 0.2 <= share <= 0.4


def test_duplicate_case_ids_are_found(tmp_path):
    line = json.dumps(
        {
            "case_id": "EV-0001",
            "split": "dev",
            "category": "exact_skill",
            "question": "Which profiles list SQL?",
            "expected_behavior": "answer",
            "corpus_requirements": "At least 2 profiles list SQL.",
        }
    )
    other = line.replace('"dev"', '"holdout"')
    path = tmp_path / "set.jsonl"
    path.write_text(line + "\n" + other + "\n", encoding="utf-8")

    cases, problems = load_golden_set(path)

    assert problems == []
    assert any("used 2 times" in problem for problem in check_cases(cases))


def test_bad_line_is_reported(tmp_path):
    path = tmp_path / "set.jsonl"
    path.write_text('{"case_id": "nope"}\nnot json\n', encoding="utf-8")

    cases, problems = load_golden_set(path)

    assert cases == []
    assert len(problems) == 2
