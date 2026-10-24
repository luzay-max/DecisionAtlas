"""Offline verification of one explicitly approved public evidence snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "engine"))

from app.extractor.upstream_verification import evaluate_public_capture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="Local Phase-A export JSON")
    parser.add_argument("--manifest", type=Path, required=True, help="Local public GitHub capture manifest JSON")
    parser.add_argument("--output", type=Path, required=True, help="New JSON report outside Git checkout")
    parser.add_argument("--approve-public-data", action="store_true", help="I verified the input and destination contain only approved public data")
    args = parser.parse_args(argv)
    if not args.approve_public_data:
        parser.error("--approve-public-data is mandatory")
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("report must be outside the Git checkout")
    if output.exists():
        parser.error("report must not exist")
    if not output.parent.is_dir():
        parser.error("report parent directory must exist")
    try:
        snapshot = json.loads(args.snapshot.expanduser().read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.expanduser().read_text(encoding="utf-8"))
        report = evaluate_public_capture(snapshot, manifest)
        with output.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(json.dumps(report["citation_status_counts"], sort_keys=True))
        return 1 if report["citation_status_counts"].get("fail", 0) else 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Verification refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
