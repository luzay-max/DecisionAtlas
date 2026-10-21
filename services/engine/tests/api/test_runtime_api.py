from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import set_runtime_provider_modes
from app.auth import AuthContext, require_actor
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

    app = create_app()
    app.dependency_overrides[require_actor] = lambda: AuthContext(actor_id=1, username="admin", owner_scope="local-default", owner_scope_id=1, role="admin", session_token="test", bootstrap=False)
    client = TestClient(app)
    response = client.post("/runtime/provider-mode", json={"mode": "live"})

    assert response.status_code == 200
    assert response.json()["mode"] == "openai_compatible"
    assert response.json()["is_live"] is True
    assert response.json()["embedding_provider_mode"] == "fake"

    set_runtime_provider_modes(llm_provider_mode=None, embedding_provider_mode=None)


def test_post_runtime_provider_mode_requires_authentication(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "false")
    client = TestClient(create_app())
    response = client.post("/runtime/provider-mode", json={"mode": "fake"})
    assert response.status_code == 401


def test_post_runtime_provider_mode_rejects_viewer() -> None:
    app = create_app()
    app.dependency_overrides[require_actor] = lambda: AuthContext(actor_id=2, username="viewer", owner_scope="local-default", owner_scope_id=1, role="viewer", session_token="test", bootstrap=False)
    assert TestClient(app).post("/runtime/provider-mode", json={"mode": "fake"}).status_code == 403
