from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[4]
    path = root / "scripts" / "ci" / "collect_candidate_precision_evidence.py"
    spec = importlib.util.spec_from_file_location("collect_candidate_precision_evidence", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_precision_evidence_compares_legacy_and_current_ordering_without_reviewing_rows():
    module = _load_module()
    rows = [
        {
            "id": 2,
            "title": "Grounded candidate",
            "confidence": 0.75,
            "candidate_ranking": {"tier": "strong", "score": 91, "is_representative": True},
        },
        {
            "id": 3,
            "title": "Near duplicate",
            "confidence": 0.72,
            "candidate_ranking": {"tier": "partial", "score": 55, "is_representative": False},
        },
        {
            "id": 1,
            "title": "High confidence but weak support",
            "confidence": 0.99,
            "candidate_ranking": {"tier": "weak", "score": 38, "is_representative": True},
        },
    ]

    evidence = module._summarize_workspace("github-example-repo", rows)

    assert evidence["before"]["decision_ids"] == [1, 2, 3]
    assert evidence["after"]["decision_ids"] == [2, 3, 1]
    assert evidence["ordering_delta"]["top_changed"] is True
    assert evidence["tier_counts"] == {"strong": 1, "partial": 1, "weak": 1}
    assert evidence["duplicate_secondary_count"] == 1
