from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import set_runtime_provider_modes
from app.main import create_app


def test_get_runtime_provider_mode_returns_fake_by_default(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_MODE", "fake")
    monkeypatch.setenv("EMBEDDING_PROVIDER_MODE", "fake")
    set_runtime_provider_modes(llm_provider_mode=None, embedding_provider_mode=None)

    client = TestClient(create_app())
    response = client.get("/runtime/provider-mode")

    assert response.status_code == 200
    assert response.json()["mode"] == "fake"
    assert response.json()["is_live"] is False


def test_post_runtime_provider_mode_switches_to_live(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_MODE", "fake")
    monkeypatch.setenv("EMBEDDING_PROVIDER_MODE", "fake")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    set_runtime_provider_modes(llm_provider_mode=None, embedding_provider_mode=None)

    client = TestClient(create_app())
    response = client.post("/runtime/provider-mode", json={"mode": "live"})

    assert response.status_code == 200
    assert response.json()["mode"] == "openai_compatible"
    assert response.json()["is_live"] is True
    assert response.json()["embedding_provider_mode"] == "fake"

    set_runtime_provider_modes(llm_provider_mode=None, embedding_provider_mode=None)
