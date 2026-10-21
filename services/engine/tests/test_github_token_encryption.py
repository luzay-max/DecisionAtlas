from __future__ import annotations

import base64
import importlib.util
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import GitHubTokenAccessSource
from app.repositories.github_token_access_sources import GitHubTokenAccessSourceRepository
from app.security.github_tokens import (
    CredentialProtectionError,
    decrypt_token,
    encrypt_token,
    is_encrypted_token,
    token_key_id,
)


def second_key() -> str:
    return base64.urlsafe_b64encode(bytes(range(32, 64))).decode("ascii")


def _context() -> dict[str, str]:
    return {"owner_scope": "team-1", "source_ref": "private-repo", "repo_identity": "org/private"}


def _setup(tmp_path: Path, monkeypatch) -> Path:
    path = tmp_path / "secrets.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    command.upgrade(cfg, "head")
    return path


def _migrator():
    path = Path(__file__).resolve().parents[3] / "scripts" / "security" / "migrate_github_tokens.py"
    spec = importlib.util.spec_from_file_location("token_migration", path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_token_is_encrypted_at_rest_and_bound_to_scope(monkeypatch) -> None:
    token = "ghp-not-a-real-production-token"
    encrypted = encrypt_token(token, **_context())
    assert is_encrypted_token(encrypted)
    assert token not in encrypted
    assert decrypt_token(encrypted, **_context()) == token
    with pytest.raises(CredentialProtectionError, match="does not match"):
        decrypt_token(encrypted, owner_scope="team-2", source_ref="private-repo", repo_identity="org/private")
    with pytest.raises(CredentialProtectionError, match="authentication failed"):
        decrypt_token(encrypted[:-1] + ("x" if encrypted[-1] != "x" else "y"), **_context())


def test_missing_or_invalid_key_fails_closed(monkeypatch) -> None:
    token = encrypt_token("fake-token", **_context())
    monkeypatch.delenv("GITHUB_TOKEN_ENCRYPTION_KEYS", raising=False)
    with pytest.raises(CredentialProtectionError, match="not configured"):
        decrypt_token(token, **_context())
    with pytest.raises(CredentialProtectionError, match="not configured"):
        encrypt_token("fake-token", **_context())
    monkeypatch.setenv("GITHUB_TOKEN_ENCRYPTION_KEYS", "invalid=too-short")
    with pytest.raises(CredentialProtectionError, match="Invalid .* configuration"):
        decrypt_token(token, **_context())
    with pytest.raises(CredentialProtectionError, match="not a supported encrypted"):
        decrypt_token("ghp-legacy-raw", **_context())


def test_repo_write_and_read_not_plaintext(tmp_path: Path, monkeypatch) -> None:
    db = _setup(tmp_path, monkeypatch)
    engine = create_engine(f"sqlite:///{db}")
    with Session(engine) as session:
        repo = GitHubTokenAccessSourceRepository(session)
        row = repo.upsert(**_context(), display_label="Private", token_secret="ghp-secret",
                          authorization_status="authorized", last_error=None, validated_at=None)
        assert row.token_secret.startswith("enc:v1:testkey:")
        assert repo.read_token(row) == "ghp-secret"
        session.commit()
    assert b"ghp-secret" not in db.read_bytes()
    engine.dispose()


def test_offline_rotation_and_legacy_migration_are_explicit_and_atomic(tmp_path: Path, monkeypatch) -> None:
    db = _setup(tmp_path, monkeypatch)
    engine = create_engine(f"sqlite:///{db}")
    with Session(engine) as session:
        repo = GitHubTokenAccessSourceRepository(session)
        encrypted = repo.upsert(**_context(), display_label="Encrypted", token_secret="ghp-encrypted",
                                authorization_status="authorized", last_error=None, validated_at=None)
        legacy = GitHubTokenAccessSource(owner_scope="team-1", source_ref="old", display_label="Old",
                                         repo_identity="org/old", token_secret="ghp-old-plaintext",
                                         authorization_status="authorized")
        session.add(legacy)
        session.commit()
        encrypted_id, legacy_id = encrypted.id, legacy.id

    old_key = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="
    monkeypatch.setenv("GITHUB_TOKEN_ENCRYPTION_KEYS", f"next={second_key()},testkey={old_key}")
    mig = _migrator()
    with pytest.raises(CredentialProtectionError, match="Legacy plaintext"):
        mig.inspect_and_rotate(apply=True, include_legacy=False)
    with Session(engine) as session:
        assert session.get(GitHubTokenAccessSource, encrypted_id).token_secret.startswith("enc:v1:testkey:")
        assert session.get(GitHubTokenAccessSource, legacy_id).token_secret == "ghp-old-plaintext"
    stats = mig.inspect_and_rotate(apply=False, include_legacy=True)
    assert stats["legacy_plaintext"] == 1 and stats["needs_rotation"] == 1 and stats["updated"] == 0
    changed = mig.inspect_and_rotate(apply=True, include_legacy=True)
    assert changed["updated"] == 2
    with Session(engine) as session:
        one = session.get(GitHubTokenAccessSource, encrypted_id)
        two = session.get(GitHubTokenAccessSource, legacy_id)
        assert token_key_id(one.token_secret) == "next"
        assert token_key_id(two.token_secret) == "next"
        assert GitHubTokenAccessSourceRepository(session).read_token(one) == "ghp-encrypted"
        assert GitHubTokenAccessSourceRepository(session).read_token(two) == "ghp-old-plaintext"
    engine.dispose()
