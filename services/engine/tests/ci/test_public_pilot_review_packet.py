"""Review packet must remain explicitly ungraded, even with real GitHub sources."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _runner():
    script = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "run_public_pilot_ci.py"
    spec = importlib.util.spec_from_file_location("real_public_pilot_report", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_review_packet_has_citation_links_but_no_automatic_quality_grade(tmp_path: Path) -> None:
    module = _runner()
    module.OUTPUT = tmp_path
    module.write_human_review_packet({
        "metrics": {
            "candidate_preview": [
                {"id": 7, "title": "Separate public and internal names",
                 "review_state": "candidate", "source_ref_count": 1},
            ],
            "review_evidence": {
                7: {
                    "problem": "Different audiences need different names",
                    "chosen_option": "Define spec independently",
                    "source_urls": ["https://github.com/pallets/click/pull/3877"],
                }
            },
        }
    })
    packet = json.loads((tmp_path / "pilot-pallets-click-review-packet.json").read_text(encoding="utf-8"))
    assert packet["quality_claim"] == "not_evaluated"
    assert packet["provider_mode"] == "fake"
    assert packet["reviewed_by_human"] is False
    assert packet["decision_sample_size"] == 1
    item = packet["decisions"][0]
    assert item["is_real_decision"] is None
    assert item["source_verified"] is None
    assert item["source_urls"] == ["https://github.com/pallets/click/pull/3877"]
    markdown = (tmp_path / "pilot-pallets-click-review-packet.md").read_text(encoding="utf-8")
    assert "FakeProvider" in markdown
    assert "not_reviewed" in markdown
    assert "https://github.com/pallets/click/pull/3877" in markdown
