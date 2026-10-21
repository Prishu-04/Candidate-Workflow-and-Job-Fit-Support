import sys
from pathlib import Path

from app.data.golden import check_cases, load_golden_set, summarize

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evals/golden_set.jsonl")

cases, problems = load_golden_set(path)
problems = problems + check_cases(cases)

summary = summarize(cases)
print(f"file: {path}")
for name, value in summary.items():
    print(f"{name}: {value}")

if problems:
    print()
    print("PROBLEMS:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)

print()
print("golden set is valid")
