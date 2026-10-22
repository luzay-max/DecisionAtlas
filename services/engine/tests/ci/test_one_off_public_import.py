from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_runner():
    script = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "rehearse_public_github_import.py"
    spec = importlib.util.spec_from_file_location("one_off_public_import", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_one_off_public_repo_uses_real_slug_without_changing_canonical_pool(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    captured: list[dict] = []

    def fake_rehearsal(**kwargs):
        captured.append(kwargs["repository"])
        return runner.build_report(
            repository=kwargs["repository"],
            base_url=kwargs["base_url"],
            setup_outcome="operator_guided",
        )

    monkeypatch.setattr(runner, "rehearse_public_import", fake_rehearsal)
    output = tmp_path / "rehearsal.json"
    markdown = tmp_path / "rehearsal.md"
    monkeypatch.setattr(
        sys, "argv", [
            "rehearse_public_github_import.py", "--repo", "pallets/click",
            "--output-json", str(output), "--output-markdown", str(markdown),
        ],
    )
    assert runner.main() == 0
    assert captured[0]["repo"] == "pallets/click"
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["setup"]["outcome"] == "operator_guided"
    assert report["repository"]["id"] == "pallets-click"
    assert markdown.is_file()


def test_one_off_public_repo_rejects_urls_and_bad_identifiers(monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(sys, "argv", [
        "rehearse_public_github_import.py", "--repo", "https://github.com/pallets/click"
    ])
    assert runner.main() == 1


def test_sqlite_writer_lock_is_classified_as_local_failure() -> None:
    runner = _load_runner()
    assert runner._failed_import_outcome({
        "status": "failed",
        "summary": {"failure_category": "analysis_execution_failed"},
    }) == "local_stack_failure"
    assert runner._failed_import_outcome({
        "status": "failed",
        "summary": {"failure_category": "provider_failure"},
    }) == "provider_failure"
