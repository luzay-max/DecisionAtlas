"""Explicit offline recovery for orphaned GitHub import jobs.

FastAPI BackgroundTasks are process-local and cannot be safely auto-replayed
after a crash. This command defaults to an inspection-only report. Only use
--apply after all application/worker processes using the DB have been stopped.

Run from services/engine after setting DATABASE_URL:
    uv run python -m app.jobs.recover_import_jobs
    uv run python -m app.jobs.recover_import_jobs --job-id <id> --apply --workers-stopped
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
import json
from typing import Sequence

from app.db.session import get_db_session
from app.repositories.import_jobs import ImportJobRepository


def _job_report(job) -> dict[str, str | int | None]:
    return {
        "job_id": job.job_id,
        "workspace_id": job.workspace_id,
        "repo": job.repo,
        "mode": job.mode,
        "status": job.status,
        "stage": (job.summary_json or {}).get("stage"),
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect possibly orphaned imports. Only an operator who has "
            "stopped ALL workers may apply recovery; never auto-replay jobs."
        )
    )
    parser.add_argument("--job-id", help="Exact job ID to recover; required with --apply")
    parser.add_argument(
        "--minimum-age-minutes", type=int, default=60,
        help="Minimum age since job start (or queue creation), default 60",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max inspection entries (1..100)")
    parser.add_argument("--apply", action="store_true", help="Mutate one identified job")
    parser.add_argument(
        "--workers-stopped", action="store_true",
        help="Explicit assertion that every process using this DB is stopped",
    )
    args = parser.parse_args(argv)
    if args.minimum_age_minutes < 1:
        parser.error("--minimum-age-minutes must be positive")
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    if args.apply and (not args.job_id or not args.workers_stopped):
        parser.error("--apply requires --job-id and --workers-stopped")
    cutoff = datetime.now(UTC) - timedelta(minutes=args.minimum_age_minutes)

    session = get_db_session()
    try:
        repo = ImportJobRepository(session)
        if not args.apply:
            candidates = repo.list_offline_recovery_candidates(
                older_than=cutoff, limit=args.limit, job_id=args.job_id
            )
            print(json.dumps({
                "mode": "dry_run", "cutoff_utc": cutoff.isoformat(),
                "warning": (
                    "Age is not proof of a dead worker. Do not apply until "
                    "all application/worker processes have been stopped."
                ),
                "candidates": [_job_report(job) for job in candidates],
            }, ensure_ascii=False))
            return 0

        try:
            job = repo.mark_interrupted_offline(
                args.job_id, older_than=cutoff, workers_stopped=True,
            )
            session.commit()
        except ValueError as exc:
            session.rollback()
            print(json.dumps({"mode": "apply", "error": str(exc)}))
            return 1
        print(json.dumps({
            "mode": "apply", "result": "marked_failed",
            "job": _job_report(job),
            "retry": "Create a NEW import job after workers have restarted.",
        }, ensure_ascii=False))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
