"""Offline Phase C packet generation, blank reviewer template and review summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "engine"))

from app.extractor.human_evidence_review import (
    blank_reviewer_template, prepare_review_packet, summarize_review_submissions,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Join Phase-A + Phase-B inputs into an unsigned review packet")
    prepare.add_argument("--snapshot", type=Path, required=True)
    prepare.add_argument("--verification", type=Path, required=True)
    template = commands.add_parser("template", help="Create a blank reviewer submission file for a packet")
    template.add_argument("--packet", type=Path, required=True)
    summary = commands.add_parser("summarize", help="Validate separate completed reviewer submissions")
    summary.add_argument("--packet", type=Path, required=True)
    summary.add_argument("--submission", type=Path, action="append", default=[])
    for command in (prepare, template, summary):
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--approve-public-data", action="store_true")

    args = parser.parse_args(argv)
    if not args.approve_public_data:
        parser.error("--approve-public-data required; first review data and privacy permissions")
    target = args.output.expanduser().resolve()
    if target == ROOT or ROOT in target.parents:
        parser.error("review data must be saved outside the Git checkout")
    if target.exists() or not target.parent.is_dir():
        parser.error("output must be new and its parent directory must exist")

    try:
        def read(path: Path) -> dict:
            value = json.loads(path.expanduser().read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("expected JSON object")
            return value

        if args.command == "prepare":
            result = prepare_review_packet(read(args.snapshot), read(args.verification))
        elif args.command == "template":
            result = blank_reviewer_template(read(args.packet))
        else:
            result = summarize_review_submissions(read(args.packet), [read(f) for f in args.submission])
        with target.open("x", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False, allow_nan=False)
            file.write("\n")
        print(json.dumps({"output_type": args.command, "human_review": result.get("human_review", "not_run")}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Phase-C offline review refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
