"""Explicit offline migration/rotation of owner-scoped GitHub tokens.

Run with Engine stopped. Never print tokens, key material, ciphertext or SQL
rows. Dry-run verifies key availability and counts; --apply writes atomically.
Legacy plaintext requires a separate --include-legacy flag.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import select

ENGINE_DIR = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.db.models import GitHubTokenAccessSource
from app.db.session import get_db_session
from app.security.github_tokens import (
    CredentialProtectionError,
    active_key_id,
    decrypt_token,
    encrypt_token,
    is_encrypted_token,
    needs_rotation,
)


def inspect_and_rotate(*, apply: bool, include_legacy: bool) -> dict[str, int]:
    primary_id = active_key_id()  # Verify keys before touching the database.
    counts = {"already_current": 0, "needs_rotation": 0, "legacy_plaintext": 0, "updated": 0}
    session = get_db_session()
    try:
        records = list(session.scalars(select(GitHubTokenAccessSource).order_by(GitHubTokenAccessSource.id)))
        for record in records:
            context = {
                "owner_scope": record.owner_scope,
                "source_ref": record.source_ref,
                "repo_identity": record.repo_identity,
            }
            stored = record.token_secret
            if is_encrypted_token(stored):
                # Authentication and binding verification, even in dry-run.
                plaintext = decrypt_token(stored, **context)
                if not needs_rotation(stored):
                    counts["already_current"] += 1
                    continue
                counts["needs_rotation"] += 1
            else:
                counts["legacy_plaintext"] += 1
                if not include_legacy:
                    raise CredentialProtectionError(
                        "Legacy plaintext tokens found; re-authorize or explicitly enable legacy migration"
                    )
                plaintext = stored
                if not plaintext:
                    raise CredentialProtectionError("Empty legacy credential cannot be migrated")
            if apply:
                record.token_secret = encrypt_token(plaintext, **context)
                counts["updated"] += 1
        if apply:
            session.commit()
        else:
            session.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline GitHub token encryption migration / key rotation")
    parser.add_argument("--apply", action="store_true", help="Write changes; without this, only validate and count")
    parser.add_argument("--include-legacy", action="store_true", help="Explicitly permit migrating legacy plaintext")
    args = parser.parse_args()
    try:
        counts = inspect_and_rotate(apply=args.apply, include_legacy=args.include_legacy)
    except CredentialProtectionError as exc:
        print(f"Credential migration blocked: {exc}", file=sys.stderr)
        return 2
    # Never output token, ciphertext, key, owner, or source identifiers.
    print(
        f"mode={'APPLY' if args.apply else 'DRY_RUN'} "
        f"current={counts['already_current']} rotate={counts['needs_rotation']} "
        f"legacy={counts['legacy_plaintext']} updated={counts['updated']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
