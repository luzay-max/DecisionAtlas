"""Explicit, read-only export of one operator-approved public SQLite workspace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "engine"))
from app.extractor.evidence_snapshot import export_workspace_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, required=True, help="Existing local SQLite database file")
    parser.add_argument("--workspace", required=True, help="Exact workspace slug")
    parser.add_argument("--output", type=Path, required=True, help="New JSON file outside repository")
    parser.add_argument("--provider-kind", choices=("unknown", "fake"), default="unknown")
    parser.add_argument("--approve-public-data", action="store_true", help="I have verified this workspace contains only publishable public data")
    args = parser.parse_args(argv)
    if not args.approve_public_data:
        parser.error("--approve-public-data is required; review workspace contents first")
    source = args.sqlite.expanduser().resolve()
    target = args.output.expanduser().resolve()
    if not source.is_file():
        parser.error("SQLite database must already exist")
    if target == ROOT or ROOT in target.parents:
        parser.error("output must be outside the Git checkout (never commit exported source text)")
    if target.exists():
        parser.error("output already exists; refusing to overwrite")
    if not target.parent.is_dir():
        parser.error("output parent directory must exist")
    if not args.workspace.strip():
        parser.error("workspace slug must be nonempty")

    def open_read_only() -> sqlite3.Connection:
        connection = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        connection.execute("PRAGMA query_only=ON")
        return connection

    engine = create_engine("sqlite://", creator=open_read_only)
    try:
        with Session(engine) as session:
            result = export_workspace_evidence(
                session,
                workspace_slug=args.workspace,
                provider_kind=args.provider_kind,
                public_data_approved=True,
            )
        # Exclusive create: never clobber prior evidence and never expose to CI.
        with target.open("x", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(json.dumps({"candidate_count": result["candidate_count"], "citation_count": result["citation_count"]}))
        return 0
    except (ValueError, OSError, sqlite3.DatabaseError) as exc:
        print(f"Evidence export refused: {exc}", file=sys.stderr)
        return 2
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
