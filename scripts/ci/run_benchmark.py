from __future__ import annotations

import json
from pathlib import Path
import sys


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    workspace_dir = root / "examples" / "demo-workspace"
    queries = load_json(workspace_dir / "queries.json")
    expected_answers = load_json(workspace_dir / "expected-answers.json")

    query_ids = [item["id"] for item in queries]
    expected_ids = [item["id"] for item in expected_answers]

    if query_ids != expected_ids:
        print("Benchmark fixture mismatch between queries and expected answers.", file=sys.stderr)
        return 1

    print(f"Loaded {len(queries)} benchmark queries.")
    for query, expected in zip(queries, expected_answers):
        print(
            f"{query['id']}: {query['question']} -> topic={expected['expected_topic']} "
            f"min_citations={expected['min_citations']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
