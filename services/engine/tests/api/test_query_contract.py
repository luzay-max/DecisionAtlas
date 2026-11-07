from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import query
from app.api.query_contract import WhyAnswerResponse
from app.auth import require_actor
from app.llm.base import ProviderConfigurationError, ProviderError
from app.main import create_app

FIXTURE = Path(__file__).resolve().parents[4] / "packages/engine-contract/fixtures/why-ok.json"


@pytest.fixture
def endpoint(monkeypatch):
    app = create_app()
    app.dependency_overrides[require_actor] = lambda: object()
    monkeypatch.setattr(query, "get_db_session", lambda: SimpleNamespace(close=lambda: None))
    monkeypatch.setattr(query, "require_workspace_role", lambda *args, **kwargs: None)
    monkeypatch.setattr(query, "build_runtime_providers", lambda: SimpleNamespace(embedder=object()))
    return TestClient(app)


def test_response_model_preserves_shared_fixture_without_inventing_null_fields(endpoint, monkeypatch):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    monkeypatch.setattr(query, "answer_why_question", lambda **kwargs: deepcopy(payload))
    response = endpoint.post("/query/why", json={"workspace_slug": "synthetic", "question": payload["question"]})
    assert response.status_code == 200
    assert response.json() == payload
    # Especially preserve chunk-backed citations and retrieval diagnostics.
    assert "source_ref_id" not in response.json()["citations"][1]
    assert response.json()["answer_context"]["retrieval"]["structural_fit"] == 21.0


@pytest.mark.parametrize("mutation", ["status", "citation", "missing", "extra"])
def test_invalid_producer_payload_is_rejected_at_http_boundary(endpoint, monkeypatch, mutation):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if mutation == "status":
        payload["status"] = "invented-status"
    elif mutation == "citation":
        payload["citations"][0]["quote"] = 42
    elif mutation == "missing":
        del payload["answer"]
    else:
        payload["answer_context"]["undocumented_evidence"] = "must not silently disappear"
    monkeypatch.setattr(query, "answer_why_question", lambda **kwargs: payload)
    from fastapi.exceptions import ResponseValidationError
    with pytest.raises(ResponseValidationError):
        endpoint.post("/query/why", json={"workspace_slug": "synthetic", "question": "why"})


def test_invalid_request_retains_fastapi_422_envelope(endpoint):
    response = endpoint.post("/query/why", json={"workspace_slug": "synthetic"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "question"]


@pytest.mark.parametrize("exception,status", [(ValueError, 404), (ProviderError, 502), (ProviderConfigurationError, 503)])
def test_documented_errors_keep_existing_detail_envelope(endpoint, monkeypatch, exception, status):
    def fail(**kwargs):
        raise exception("synthetic failure")
    monkeypatch.setattr(query, "answer_why_question", fail)
    response = endpoint.post("/query/why", json={"workspace_slug": "synthetic", "question": "why"})
    assert response.status_code == status
    assert response.json() == {"detail": "synthetic failure"}


def test_openapi_models_request_success_and_error_responses():
    schema = create_app().openapi()
    op = schema["paths"]["/query/why"]["post"]
    assert op["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith("/WhyQueryRequest")
    assert op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith("/WhyAnswerResponse")
    assert {"200", "401", "403", "404", "422", "502", "503"} <= op["responses"].keys()
    assert "retrieval" in schema["components"]["schemas"]["WhyAnswerContext"]["properties"]
    # The current producer can emit sparse negative responses without adding
    # primary_decision/supporting_context or manufacturing citation identifiers.
    sparse = {"status": "review_required", "question": "why", "answer": "Review first", "citations": [],
              "answer_context": {"workspace_mode": "imported", "source_summary": "synthetic"}}
    assert WhyAnswerResponse.model_validate(sparse).model_dump(exclude_unset=True) == sparse
