"""Ephemeral, real SQLite backup -> migration -> rotation -> restore rehearsal.

Synthetic tokens and keys only. Neither databases nor keys are uploaded or
printed. This does not exercise a customer's own database or secret manager.
"""
from __future__ import annotations

from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory

from alembic import command
from alembic.config import Config
from cryptography.fernet import Fernet
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = ROOT / "services" / "engine"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from app.db.models import GitHubTokenAccessSource
from app.db.session import get_db_session, get_engine
from app.repositories.github_token_access_sources import GitHubTokenAccessSourceRepository
from app.security.github_tokens import CredentialProtectionError, decrypt_token


def backup_sqlite(source: Path, target: Path) -> None:
    """Use the SQLite online backup API, not a raw copy of a possibly WAL DB."""
    with closing(sqlite3.connect(str(source))) as current:
        with closing(sqlite3.connect(str(target))) as saved:
            current.backup(saved)


def rows(path: Path) -> dict[str, str]:
    with closing(sqlite3.connect(str(path))) as db:
        return dict(db.execute("SELECT source_ref, token_secret FROM github_token_access_sources"))


def migrate(db: Path, keyring: str, *, apply: bool, include_legacy: bool) -> tuple[int, str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db.as_posix()}"
    env["GITHUB_TOKEN_ENCRYPTION_KEYS"] = keyring
    args = [sys.executable, str(ROOT / "scripts/security/migrate_github_tokens.py")]
    if apply:
        args.append("--apply")
    if include_legacy:
        args.append("--include-legacy")
    proc = subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # The migration prints only non-sensitive counts; never log raw exception text.
    return proc.returncode, proc.stdout.strip()


def run() -> dict:
    output = ROOT / ".tmp" / "security-rehearsal"
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "scenario": "synthetic_sqlite_backup_migrate_rotate_restore",
        "scope": "synthetic_only",
        "status": "fail",
        "checks": {},
        "limitations": [
            "No customer database, production secrets, private GitHub API or KMS used",
            "Does not prove PostgreSQL restore, online rotation or production disaster recovery",
        ],
        "commit": os.environ.get("GITHUB_SHA", "local"),
    }
    original_url = os.environ.get("DATABASE_URL")
    original_keys = os.environ.get("GITHUB_TOKEN_ENCRYPTION_KEYS")
    try:
        with TemporaryDirectory(prefix="decisionatlas-credential-recovery-") as tempdir:
            directory = Path(tempdir)
            primary = directory / "primary.db"
            before = directory / "pre-migration-backup.db"
            after = directory / "encrypted-backup.db"
            restored = directory / "restored.db"

            old_key = Fernet.generate_key().decode("ascii")
            new_key = Fernet.generate_key().decode("ascii")
            old_ring = f"old={old_key}"
            transition_ring = f"new={new_key},old={old_key}"
            new_ring = f"new={new_key}"
            os.environ["DATABASE_URL"] = f"sqlite:///{primary.as_posix()}"
            os.environ["GITHUB_TOKEN_ENCRYPTION_KEYS"] = old_ring
            config = Config(str(ENGINE_ROOT / "alembic.ini"))
            config.set_main_option("script_location", str(ENGINE_ROOT / "alembic"))
            config.set_main_option("sqlalchemy.url", f"sqlite:///{primary.as_posix()}")
            command.upgrade(config, "head")

            synthetic_new = "synthetic-previously-encrypted-value"
            synthetic_legacy = "synthetic-legacy-plaintext-value"
            with get_db_session() as session:
                repository = GitHubTokenAccessSourceRepository(session)
                repository.upsert(
                    owner_scope="test-owner",
                    source_ref="encrypted",
                    display_label="Synthetic encrypted source",
                    repo_identity="example/private",
                    token_secret=synthetic_new,
                    authorization_status="authorized",
                    last_error=None,
                    validated_at=None,
                )
                session.add(GitHubTokenAccessSource(
                    owner_scope="test-owner",
                    source_ref="legacy",
                    display_label="Synthetic old source",
                    repo_identity="example/private",
                    token_secret=synthetic_legacy,
                    authorization_status="authorized",
                ))
                session.commit()
            # SQLAlchemy's SQLite connection pool otherwise keeps Windows DB files open.
            get_engine().dispose()

            backup_sqlite(primary, before)
            original_rows = rows(before)
            report["checks"]["sqlite_backup_contains_two_seed_rows"] = len(original_rows) == 2

            # No --include-legacy must fail atomically even when it could rotate another row.
            failed_code, _ = migrate(primary, transition_ring, apply=True, include_legacy=False)
            unchanged = rows(primary)
            report["checks"]["legacy_migration_requires_opt_in_and_rolls_back"] = (
                failed_code != 0 and unchanged == original_rows
            )
            dry_code, dry_output = migrate(primary, transition_ring, apply=False, include_legacy=True)
            report["checks"]["dry_run_is_read_only"] = (
                dry_code == 0 and rows(primary) == original_rows
                and "rotate=1" in dry_output and "legacy=1" in dry_output
            )
            applied_code, applied_output = migrate(primary, transition_ring, apply=True, include_legacy=True)
            encrypted_rows = rows(primary)
            report["checks"]["explicit_migration_encrypts_both_records"] = (
                applied_code == 0
                and "updated=2" in applied_output
                and len(encrypted_rows) == 2
                and all(value.startswith("enc:v1:new:") for value in encrypted_rows.values())
                and all(synthetic not in str(encrypted_rows) for synthetic in (synthetic_new, synthetic_legacy))
            )

            # Simulate dropping the old key, then check the restored encrypted backup.
            os.environ["GITHUB_TOKEN_ENCRYPTION_KEYS"] = new_ring
            old_envelope = original_rows["encrypted"]
            try:
                decrypt_token(
                    old_envelope,
                    owner_scope="test-owner", source_ref="encrypted", repo_identity="example/private",
                )
                report["checks"]["old_key_removed_rejects_old_ciphertext"] = False
            except CredentialProtectionError:
                report["checks"]["old_key_removed_rejects_old_ciphertext"] = True

            backup_sqlite(primary, after)
            backup_sqlite(after, restored)
            restored_rows = rows(restored)
            report["checks"]["restored_backup_matches_primary"] = restored_rows == encrypted_rows
            expected = {"encrypted": synthetic_new, "legacy": synthetic_legacy}
            report["checks"]["restored_tokens_decrypt_with_new_key_only"] = (
                len(restored_rows) == len(expected)
                and all(
                    decrypt_token(value, owner_scope="test-owner", source_ref=source,
                                  repo_identity="example/private") == expected[source]
                    for source, value in restored_rows.items()
                )
            )

            final_code, final_output = migrate(restored, new_ring, apply=False, include_legacy=False)
            report["checks"]["restored_database_passes_migration_preflight"] = (
                final_code == 0 and "rotate=0" in final_output and "legacy=0" in final_output
            )
            report["status"] = "pass" if all(report["checks"].values()) else "fail"
    except Exception as exc:
        # A backup/cleanup error must override any earlier passing assertions.
        report["status"] = "fail"
        # Only the class name, no secrets, path values, token content or exception payload.
        report["error_category"] = type(exc).__name__
    finally:
        if original_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_url
        if original_keys is None:
            os.environ.pop("GITHUB_TOKEN_ENCRYPTION_KEYS", None)
        else:
            os.environ["GITHUB_TOKEN_ENCRYPTION_KEYS"] = original_keys
        report_path = output / "result.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        lines = [
            "# Synthetic GitHub credential disaster recovery rehearsal",
            "",
            f"- Status: **{report['status']}**",
            f"- Revision: `{report['commit']}`",
            "- No production credentials or customer databases used",
            (
                "- Temporary SQLite databases and generated keys were cleaned up successfully"
                if report["status"] == "pass"
                else "- Cleanup or a validation step failed; inspect the error category and CI runner state"
            ),
            "",
            "## Checks",
            "",
        ]
        lines.extend(f"- {'PASS' if valid else 'FAIL'} — {name}" for name, valid in report["checks"].items())
        if report.get("error_category"):
            lines.append("- Error category: " + report["error_category"])
        lines.extend(["", "## Limits", ""])
        lines.extend(f"- {limit}" for limit in report["limitations"])
        (output / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Synthetic credential backup/restore rehearsal: " + report["status"])
    return report


if __name__ == "__main__":
    raise SystemExit(0 if run()["status"] == "pass" else 1)
