"""The demo bootstrap is an explicit test-only setting, never a production default."""

import pytest


@pytest.fixture(autouse=True)
def enable_local_test_bootstrap(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_AUTO_BOOTSTRAP_LOCAL", "true")
    # Public, deterministic fixture key ONLY: never use for deployed credentials.
    monkeypatch.setenv("GITHUB_TOKEN_ENCRYPTION_KEYS", "testkey=AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=")
