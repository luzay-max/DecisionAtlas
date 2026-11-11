from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import GitHubAppInstallation, Workspace


def _config_for(url: str, monkeypatch) -> Config:
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_d1b_backfills_repository_and_scope_quarantines_and_preserves_history(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'd1b-backfill.db'}"
    config = _config_for(url, monkeypatch)
    command.upgrade(config, "0013_import_job_lifecycle")
    engine = create_engine(url)

    with Session(engine) as session:
        first = Workspace(
            slug="d1b-first", name="First alias", owner_scope="scope-repo",
            repo_identity="Acme/DecisionAtlas",
        )
        second = Workspace(
            slug="d1b-second", name="Second alias", owner_scope="scope-repo",
        )
        unknown = Workspace(
            slug="d1b-unknown", name="Unknown identity", owner_scope="scope-wide",
        )
        session.add_all([first, second, unknown])
        session.flush()
        session.execute(
            text(
                "INSERT INTO import_jobs "
                "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                "VALUES (:job_id, :workspace_id, :repo, 'full', 'queued', 'manual', 0)"
            ),
            [
                {
                    "job_id": "d1b-legacy-one",
                    "workspace_id": first.id,
                    "repo": "https://github.com/acme/decisionatlas.git",
                },
                {
                    "job_id": "d1b-legacy-two",
                    "workspace_id": second.id,
                    "repo": "ACME/DECISIONATLAS",
                },
                {
                    "job_id": "d1b-legacy-unknown",
                    "workspace_id": unknown.id,
                    "repo": "https://gitlab.example/acme/private",
                },
            ],
        )
        session.add(
            GitHubAppInstallation(
                owner_scope="scope-repo",
                installation_id="9001",
                account_login="acme",
                account_type="Organization",
            )
        )
        session.commit()

    command.upgrade(config, "head")
    with engine.connect() as connection:
        quarantines = connection.execute(
            text(
                "SELECT owner_scope, scope_kind, canonical_repo_key, status, reason_code "
                "FROM import_history_quarantines ORDER BY owner_scope"
            )
        ).mappings().all()
        assert [dict(row) for row in quarantines] == [
            {
                "owner_scope": "scope-repo",
                "scope_kind": "repository",
                "canonical_repo_key": "acme/decisionatlas",
                "status": "active",
                "reason_code": "legacy_history_unverified",
            },
            {
                "owner_scope": "scope-wide",
                "scope_kind": "owner_scope",
                "canonical_repo_key": None,
                "status": "active",
                "reason_code": "legacy_history_unverified",
            },
        ]
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_jobs WHERE protocol_version='legacy'")
        ) == 3
        assert connection.scalar(
            text("SELECT COUNT(*) FROM github_app_installations WHERE installation_id='9001'")
        ) == 1
        tables = set(inspect(connection).get_table_names())
        assert {"import_history_quarantines", "github_webhook_deliveries"}.issubset(tables)
        indexes = {item["name"] for item in inspect(connection).get_indexes("github_app_installations")}
        assert "uq_github_app_installations_installation_id" in indexes

    with Session(engine) as session:
        session.execute(
            text(
                "INSERT INTO github_webhook_deliveries "
                "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition) "
                "VALUES ('9001', 'delivery-1', 'scope-repo', 'push', :digest, 'quarantined')"
            ),
            {"digest": "a" * 64},
        )
        session.commit()

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, event_name, payload_sha256, disposition) "
                    "VALUES ('9001', 'delivery-1', 'push', :digest, 'quarantined')"
                ),
                {"digest": "a" * 64},
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, event_name, payload_sha256, disposition) "
                    "VALUES ('9001', 'delivery-1', 'push', :digest, 'quarantined')"
                ),
                {"digest": "b" * 64},
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, event_name, payload_sha256, disposition) "
                    "VALUES ('9001', 'delivery-2', 'push', 'short', 'quarantined')"
                )
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, event_name, payload_sha256, disposition) "
                    "VALUES ('9001', '', 'push', :digest, 'quarantined')"
                ),
                {"digest": "a" * 64},
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, event_name, payload_sha256, disposition) "
                    "VALUES ('9001', 'delivery-3', 'push', :digest, 'quarantined')"
                ),
                {"digest": "A" * 64},
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO github_app_installations "
                    "(owner_scope, installation_id) VALUES ('other-scope', '9001')"
                )
            )

    with pytest.raises(RuntimeError, match="force transaction rollback"):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO import_jobs "
                    "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                    "VALUES ('d1b-atomic-rollback', :workspace_id, 'acme/decisionatlas', "
                    "'full', 'queued', 'webhook', 0)"
                ),
                {"workspace_id": first.id},
            )
            connection.execute(
                text(
                    "INSERT INTO github_webhook_deliveries "
                    "(installation_id, delivery_id, owner_scope, event_name, payload_sha256, disposition, job_id) "
                    "VALUES ('9001', 'delivery-rollback', 'scope-repo', 'push', :digest, 'queued', "
                    "'d1b-atomic-rollback')"
                ),
                {"digest": "d" * 64},
            )
            raise RuntimeError("force transaction rollback")

    with engine.connect() as connection:
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_jobs WHERE job_id='d1b-atomic-rollback'")
        ) == 0
        assert connection.scalar(
            text("SELECT COUNT(*) FROM github_webhook_deliveries WHERE delivery_id='delivery-rollback'")
        ) == 0

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO import_history_quarantines "
                    "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                    "VALUES ('scope-repo', 'repository', 'acme/decisionatlas', "
                    "'active', 'duplicate-active')"
                )
            )

    # Duplicate scope-wide active rows are rejected. A repository-specific row
    # may coexist, so the runtime gate must always check scope-wide isolation too.
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO import_history_quarantines "
                    "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                    "VALUES ('scope-wide', 'owner_scope', NULL, 'active', 'duplicate-scope')"
                )
            )

    # Clearance requires operator identity, time and a non-empty rationale.
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE import_history_quarantines SET status='cleared' "
                    "WHERE owner_scope='scope-repo'"
                )
            )

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE import_history_quarantines "
                "SET status='cleared', cleared_at=CURRENT_TIMESTAMP, "
                "cleared_by='operator@example.test', "
                "clearance_rationale='Reviewed historical partial results' "
                "WHERE owner_scope='scope-repo' AND scope_kind='repository'"
            )
        )
        connection.execute(
            text(
                "INSERT INTO import_history_quarantines "
                "(owner_scope, scope_kind, canonical_repo_key, status, reason_code) "
                "VALUES ('scope-repo', 'repository', 'acme/decisionatlas', "
                "'active', 'newly-discovered-legacy-source')"
            )
        )
    with engine.connect() as connection:
        assert connection.scalar(
            text(
                "SELECT COUNT(*) FROM import_history_quarantines "
                "WHERE owner_scope='scope-repo' AND status='cleared'"
            )
        ) == 1
        assert connection.scalar(
            text(
                "SELECT COUNT(*) FROM import_history_quarantines "
                "WHERE owner_scope='scope-repo' AND status='active'"
            )
        ) == 1

    command.downgrade(config, "0013_import_job_lifecycle")
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())
        assert "import_history_quarantines" not in tables
        assert "github_webhook_deliveries" not in tables
        assert connection.scalar(
            text("SELECT COUNT(*) FROM import_jobs WHERE protocol_version='legacy'")
        ) == 3
        assert connection.scalar(
            text("SELECT COUNT(*) FROM github_app_installations WHERE installation_id='9001'")
        ) == 1
    engine.dispose()


def test_d1b_migration_fails_closed_on_duplicate_installation_ids(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'd1b-duplicate-installation.db'}"
    config = _config_for(url, monkeypatch)
    command.upgrade(config, "0013_import_job_lifecycle")
    engine = create_engine(url)
    with Session(engine) as session:
        session.add_all(
            [
                GitHubAppInstallation(owner_scope="scope-a", installation_id="duplicate-1"),
                GitHubAppInstallation(owner_scope="scope-b", installation_id="duplicate-1"),
            ]
        )
        session.commit()

    with pytest.raises(RuntimeError, match="duplicate GitHub installation_id"):
        command.upgrade(config, "head")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "0013_import_job_lifecycle"
        )
        tables = set(inspect(connection).get_table_names())
        assert "import_history_quarantines" not in tables
        assert "github_webhook_deliveries" not in tables
    engine.dispose()


def test_d1b_migration_fails_closed_when_legacy_owner_scope_is_unresolved(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'd1b-unresolved-owner.db'}"
    config = _config_for(url, monkeypatch)
    command.upgrade(config, "0013_import_job_lifecycle")
    engine = create_engine(url)
    with Session(engine) as session:
        workspace = Workspace(
            slug="d1b-no-owner", name="Missing owner scope", owner_scope="temporary",
        )
        session.add(workspace)
        session.flush()
        session.execute(
            text(
                "INSERT INTO import_jobs "
                "(job_id, workspace_id, repo, mode, status, sync_origin, imported_count) "
                "VALUES ('d1b-orphan-scope', :workspace_id, 'acme/repo', "
                "'full', 'queued', 'manual', 0)"
            ),
            {"workspace_id": workspace.id},
        )
        session.execute(
            text("UPDATE workspaces SET owner_scope='' WHERE id=:workspace_id"),
            {"workspace_id": workspace.id},
        )
        session.commit()

    with pytest.raises(RuntimeError, match="unresolved workspace/owner scope"):
        command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "0013_import_job_lifecycle"
        )
    engine.dispose()



def test_d1b_migration_fails_closed_on_empty_installation_identity(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'd1b-empty-installation.db'}"
    config = _config_for(url, monkeypatch)
    command.upgrade(config, "0013_import_job_lifecycle")
    engine = create_engine(url)
    with Session(engine) as session:
        session.add(
            GitHubAppInstallation(owner_scope="scope-empty", installation_id=" ")
        )
        session.commit()

    with pytest.raises(RuntimeError, match="empty installation_id"):
        command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            "0013_import_job_lifecycle"
        )
    engine.dispose()
