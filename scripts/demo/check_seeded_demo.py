from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

ENGINE_DIR = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.config import get_settings
from app.db.models import Decision, DriftAlert, SourceRef, Workspace


DEMO_WORKSPACE_SLUG = "demo-workspace"


@dataclass(frozen=True)
class SeededDemoReadiness:
    ready: bool
    workspace_present: bool
    accepted_decision_count: int
    candidate_decision_count: int
    source_ref_count: int
    timeline_decision_count: int
    open_drift_alert_count: int
    recommended_recovery: str | None
    summary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def check_seeded_demo_readiness(database_url: str | None = None) -> SeededDemoReadiness:
    settings = get_settings()
    engine = create_engine(database_url or settings.database_url)

    try:
        with Session(engine) as session:
            workspace = session.scalar(select(Workspace).where(Workspace.slug == DEMO_WORKSPACE_SLUG))
            if workspace is None:
                return SeededDemoReadiness(
                    ready=False,
                    workspace_present=False,
                    accepted_decision_count=0,
                    candidate_decision_count=0,
                    source_ref_count=0,
                    timeline_decision_count=0,
                    open_drift_alert_count=0,
                    recommended_recovery="reset",
                    summary="Seeded demo workspace is missing. Run reset-demo.ps1; use reseed-demo.ps1 if migrations or schema drift are suspected.",
                )

            accepted_count = _count(
                session,
                select(func.count())
                .select_from(Decision)
                .where(Decision.workspace_id == workspace.id, Decision.review_state == "accepted"),
            )
            candidate_count = _count(
                session,
                select(func.count())
                .select_from(Decision)
                .where(Decision.workspace_id == workspace.id, Decision.review_state == "candidate"),
            )
            source_ref_count = _count(
                session,
                select(func.count())
                .select_from(SourceRef)
                .join(Decision, SourceRef.decision_id == Decision.id)
                .where(Decision.workspace_id == workspace.id, Decision.review_state == "accepted"),
            )
            timeline_count = _count(
                session,
                select(func.count())
                .select_from(Decision)
                .where(
                    Decision.workspace_id == workspace.id,
                    Decision.review_state == "accepted",
                    Decision.created_at.is_not(None),
                ),
            )
            drift_count = _count(
                session,
                select(func.count())
                .select_from(DriftAlert)
                .where(DriftAlert.workspace_id == workspace.id, DriftAlert.status == "open"),
            )
    except SQLAlchemyError as exc:
        return SeededDemoReadiness(
            ready=False,
            workspace_present=False,
            accepted_decision_count=0,
            candidate_decision_count=0,
            source_ref_count=0,
            timeline_decision_count=0,
            open_drift_alert_count=0,
            recommended_recovery="reseed",
            summary=f"Seeded demo readiness could not query the database ({exc.__class__.__name__}). Run reseed-demo.ps1 after verifying migrations and DATABASE_URL.",
        )
    finally:
        engine.dispose()

    ready = all(
        [
            accepted_count > 0,
            candidate_count > 0,
            source_ref_count > 0,
            timeline_count > 0,
            drift_count > 0,
        ]
    )
    if ready:
        recovery = None
        summary = "Seeded demo lane is walkthrough-ready."
    else:
        recovery = "reset"
        summary = (
            "Seeded demo lane is not walkthrough-ready. Run reset-demo.ps1 to restore demo-workspace; "
            "use reseed-demo.ps1 if reset fails or migrations/database drift are suspected."
        )

    return SeededDemoReadiness(
        ready=ready,
        workspace_present=True,
        accepted_decision_count=accepted_count,
        candidate_decision_count=candidate_count,
        source_ref_count=source_ref_count,
        timeline_decision_count=timeline_count,
        open_drift_alert_count=drift_count,
        recommended_recovery=recovery,
        summary=summary,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check seeded demo walkthrough readiness.")
    parser.add_argument("--database-url", help="Database URL override. Defaults to DATABASE_URL/settings.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--no-fail", action="store_true", help="Return 0 even when the seeded demo is not ready.")
    args = parser.parse_args(argv)

    result = check_seeded_demo_readiness(database_url=args.database_url)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Seeded demo ready: {str(result.ready).lower()}")
        print(result.summary)
        print(
            "Counts: "
            f"accepted={result.accepted_decision_count}, "
            f"candidate={result.candidate_decision_count}, "
            f"source_refs={result.source_ref_count}, "
            f"timeline={result.timeline_decision_count}, "
            f"open_drift_alerts={result.open_drift_alert_count}"
        )
        if result.recommended_recovery:
            print(f"Recommended recovery: {result.recommended_recovery}")

    return 0 if result.ready or args.no_fail else 1


def _count(session: Session, statement) -> int:
    return int(session.scalar(statement) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
