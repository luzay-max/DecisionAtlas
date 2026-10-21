"""Versioned, authenticated encryption for owner-scoped GitHub access tokens.

Keys are separate from the database and never logged. Stored envelopes bind
the authenticated token to its owner scope, source ref, and repository.
"""
from __future__ import annotations

import json
import re

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


PREFIX = "enc:v1:"
KEY_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class CredentialProtectionError(Exception):
    """An intentionally non-secret-bearing encryption or key configuration error."""


def _keyring() -> list[tuple[str, Fernet]]:
    configured = get_settings().github_token_encryption_keys
    if not configured or not configured.strip():
        raise CredentialProtectionError("GitHub token encryption keys are not configured")
    keys: list[tuple[str, Fernet]] = []
    seen: set[str] = set()
    for part in configured.split(","):
        label, separator, encoded_key = part.strip().partition("=")
        if not separator or not KEY_ID_RE.fullmatch(label) or label in seen:
            raise CredentialProtectionError("Invalid GitHub token encryption key configuration")
        try:
            key = Fernet(encoded_key.strip().encode("ascii"))
        except (ValueError, TypeError, UnicodeError) as exc:
            raise CredentialProtectionError("Invalid GitHub token encryption key configuration") from exc
        keys.append((label, key))
        seen.add(label)
    return keys


def active_key_id() -> str:
    return _keyring()[0][0]


def is_encrypted_token(value: str) -> bool:
    return value.startswith("enc:")


def token_key_id(value: str) -> str:
    if not value.startswith(PREFIX):
        raise CredentialProtectionError("Stored GitHub credential is not a supported encrypted token")
    try:
        label, ciphertext = value[len(PREFIX):].split(":", 1)
    except ValueError as exc:
        raise CredentialProtectionError("Stored GitHub credential has an invalid envelope") from exc
    if not KEY_ID_RE.fullmatch(label) or not ciphertext:
        raise CredentialProtectionError("Stored GitHub credential has an invalid envelope")
    return label


def encrypt_token(token: str, *, owner_scope: str, source_ref: str, repo_identity: str) -> str:
    if not token or is_encrypted_token(token):
        raise CredentialProtectionError("Invalid raw GitHub access token")
    label, fernet = _keyring()[0]
    payload = {
        "version": 1,
        "owner_scope": owner_scope,
        "source_ref": source_ref,
        "repo_identity": repo_identity,
        "token": token,
    }
    ciphertext = fernet.encrypt(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{PREFIX}{label}:{ciphertext.decode('ascii')}"


def decrypt_token(envelope: str, *, owner_scope: str, source_ref: str, repo_identity: str) -> str:
    label = token_key_id(envelope)
    try:
        ciphertext = envelope[len(PREFIX):].split(":", 1)[1].encode("ascii")
    except (IndexError, UnicodeError) as exc:
        raise CredentialProtectionError("Stored GitHub credential has an invalid envelope") from exc
    keys = dict(_keyring())
    if label not in keys:
        raise CredentialProtectionError("Required GitHub credential key is unavailable")
    try:
        payload = json.loads(keys[label].decrypt(ciphertext).decode("utf-8"))
    except (InvalidToken, ValueError, TypeError, UnicodeError) as exc:
        raise CredentialProtectionError("Stored GitHub credential authentication failed") from exc
    if not isinstance(payload, dict) or (
        payload.get("version") != 1
        or payload.get("owner_scope") != owner_scope
        or payload.get("source_ref") != source_ref
        or payload.get("repo_identity") != repo_identity
        or not isinstance(payload.get("token"), str)
        or not payload["token"]
    ):
        raise CredentialProtectionError("Stored GitHub credential does not match its access source")
    return payload["token"]


def needs_rotation(value: str) -> bool:
    return token_key_id(value) != _keyring()[0][0]
