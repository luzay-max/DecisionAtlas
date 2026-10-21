"""All DeepSeek tests are offline and cannot access a billable API."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from app.llm.base import ExtractionRequest
from app.llm.openai_compatible import OpenAICompatibleProvider


def _pilot():
    path = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "deepseek_pilot.py"
    spec = importlib.util.spec_from_file_location("deepseek_pilot_dry", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dry_run_never_calls_deepseek_and_exports_ungraded_public_citations(tmp_path, monkeypatch) -> None:
    pilot = _pilot()
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_PILOT_APPROVED", raising=False)
    report = pilot.run(live=False, output_dir=tmp_path)
    assert report["status"] == "mock_format_pass"
    assert report["mode"] == "dry_run_mock"
    assert report["billing"]["paid_calls_attempted"] == 0
    assert len(report["samples"]) == 2
    assert all(s["source"] == "synthetic_dry_run" for s in report["samples"])
    assert all(s["quote_exactly_in_input"] for s in report["samples"])
    assert all(s["human_assessment"] == "not_reviewed" for s in report["samples"])
    assert all(s["url"].startswith("https://github.com/pallets/click/pull/") for s in report["samples"])
    output = json.loads((tmp_path / "deepseek-pilot-summary.json").read_text(encoding="utf-8"))
    assert output["why_search"] == "not_run"
    assert output["drift"] == "not_run"
    assert "mock_format_pass" in (tmp_path / "deepseek-pilot-summary.md").read_text(encoding="utf-8")


def test_live_mode_refuses_any_call_without_separate_authorization(tmp_path, monkeypatch) -> None:
    pilot = _pilot()
    monkeypatch.setenv("DEEPSEEK_API_KEY", "synthetic-not-a-real-key")
    monkeypatch.delenv("DEEPSEEK_PILOT_APPROVED", raising=False)
    report = pilot.run(live=True, output_dir=tmp_path)
    assert report["status"] == "blocked"
    assert report["error_category"] == "PilotGuardError"
    assert report["billing"]["paid_calls_attempted"] == 0
    assert "synthetic-not-a-real-key" not in json.dumps(report)


def test_live_mode_missing_key_is_blocked(tmp_path, monkeypatch) -> None:
    pilot = _pilot()
    monkeypatch.setenv("DEEPSEEK_PILOT_APPROVED", pilot.APPROVAL)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    report = pilot.run(live=True, output_dir=tmp_path)
    assert report["status"] == "blocked"
    assert report["billing"]["paid_calls_attempted"] == 0


def test_provider_uses_deepseek_model_explicit_thinking_and_output_cap() -> None:
    pilot = _pilot()
    guarded = pilot.GuardedChatClient(live=False, api_key=None)
    provider = OpenAICompatibleProvider(
        api_key="unused", model=pilot.MODEL, base_url=pilot.API_BASE,
        client=guarded, max_output_tokens=pilot.MAX_OUTPUT_TOKENS,
        disable_thinking=True,
    )
    text = provider.extract_candidate(ExtractionRequest(
        artifact_id=3877, artifact_title="test", artifact_content="PR #3877 " + pilot.DRY_FIXTURES[3877]["body"],
        prompt=pilot.PROMPT,
    ))
    assert json.loads(text)["support_quote"] == pilot.DRY_FIXTURES[3877]["quote"]
    assert guarded.calls == 1
    guarded.close()


def test_request_transport_rejects_wrong_model_thinking_oversize_and_third_call() -> None:
    pilot = _pilot()
    guarded = pilot.GuardedChatClient(live=False, api_key=None)
    request = {
        "model": pilot.MODEL, "max_tokens": pilot.MAX_OUTPUT_TOKENS,
        "thinking": {"type": "disabled"},
        "messages": [{"role": "user", "content": "PR #3877"}],
    }
    with pytest.raises(pilot.PilotGuardError, match="fixed"):
        guarded.post("/chat/completions", json={**request, "model": "deepseek-v4-pro"})
    with pytest.raises(pilot.PilotGuardError, match="Non-thinking"):
        guarded.post("/chat/completions", json={**request, "thinking": {"type": "enabled"}})
    with pytest.raises(pilot.PilotGuardError, match="size"):
        guarded.post("/chat/completions", json={**request, "messages": [
            {"role": "user", "content": "X" * 7000},
        ]})
    assert guarded.calls == 0
    assert guarded.post("/chat/completions", json=request).status_code == 200
    assert guarded.post("/chat/completions", json=request).status_code == 200
    with pytest.raises(pilot.PilotGuardError, match="Maximum paid request"):
        guarded.post("/chat/completions", json=request)
    assert guarded.calls == 2
    guarded.close()


def test_public_sample_allowlist_rejects_unexpected_pr_without_network() -> None:
    pilot = _pilot()
    with pytest.raises(pilot.PilotGuardError, match="allowlist"):
        pilot.get_public_pr(1, live=False)
