from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SCHEMA_VERSION = 1
DEFAULT_BASE_URL = "http://127.0.0.1:3001"
DEFAULT_WORKSPACES = [
    "github-jazzband-pip-tools",
    "github-pallets-markupsafe",
]
DEFAULT_OUTPUT_JSON = Path(".tmp/candidate-precision-real-repo-evidence.json")
DEFAULT_OUTPUT_MARKDOWN = Path(".tmp/candidate-precision-real-repo-evidence.md")
TIER_ORDER = {"strong": 0, "partial": 1, "weak": 2}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fetch_json(base_url: str, path: str) -> Any:
    request = Request(f"{base_url.rstrip('/')}{path}", headers={"accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _candidate_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError("Candidate API response must be a JSON array.")
    return [row for row in payload if isinstance(row, dict)]


def _legacy_sort_key(row: dict[str, Any]) -> tuple[float, int]:
    return (-float(row.get("confidence") or 0), int(row.get("id") or 0))


def _ordered_ids(rows: list[dict[str, Any]], key) -> list[int]:
    return [int(row["id"]) for row in sorted(rows, key=key) if row.get("id") is not None]


def _summarize_workspace(workspace_slug: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    before = _ordered_ids(rows, _legacy_sort_key)
    after = [int(row["id"]) for row in rows if row.get("id") is not None]
    before_position = {decision_id: index for index, decision_id in enumerate(before)}
    after_position = {decision_id: index for index, decision_id in enumerate(after)}
    moved_up = [decision_id for decision_id in after if after_position[decision_id] < before_position[decision_id]]
    moved_down = [decision_id for decision_id in before if after_position[decision_id] > before_position[decision_id]]
    rankings = [row.get("candidate_ranking") for row in rows if isinstance(row.get("candidate_ranking"), dict)]
    tier_counts = {tier: sum(1 for ranking in rankings if ranking.get("tier") == tier) for tier in TIER_ORDER}
    duplicate_count = sum(1 for ranking in rankings if ranking.get("is_representative") is False)
    top_candidate = next(
        (
            {
                "id": row.get("id"),
                "title": row.get("title"),
                "candidate_ranking": row.get("candidate_ranking"),
            }
            for row in rows
            if row.get("id") is not None
        ),
        None,
    )
    return {
        "workspace_slug": workspace_slug,
        "candidate_count": len(rows),
        "before": {
            "ordering": "legacy_confidence_desc_id_asc",
            "decision_ids": before,
        },
        "after": {
            "ordering": "precision_tier_score_confidence_id",
            "decision_ids": after,
        },
        "ordering_delta": {
            "top_changed": bool(before and after and before[0] != after[0]),
            "moved_up": moved_up,
            "moved_down": moved_down,
        },
        "tier_counts": tier_counts,
        "duplicate_secondary_count": duplicate_count,
        "top_candidate": top_candidate,
    }


def collect_live(*, base_url: str, workspace_slugs: list[str], generated_at: str) -> dict[str, Any]:
    workspaces = []
    for workspace_slug in workspace_slugs:
        query = urlencode({"workspace_slug": workspace_slug, "review_state": "candidate"})
        rows = _candidate_rows(fetch_json(base_url, f"/decisions?{query}"))
        workspaces.append(_summarize_workspace(workspace_slug, rows))
    provider_mode = fetch_json(base_url, "/runtime/provider-mode")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "commit": _git_commit(),
        "base_url": base_url,
        "comparison_basis": (
            "Before is reconstructed from the live candidate payload using the pre-change confidence ordering; "
            "after is the precision-ranked API ordering. This is not a historical snapshot."
        ),
        "provider_mode": provider_mode if isinstance(provider_mode, dict) else {"raw": provider_mode},
        "workspaces": workspaces,
        "status": "pass",
        "sensitive_material_note": "Evidence contains bounded IDs, titles, scores, and status only; no tokens or raw model output.",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Candidate Precision Real-Repository Evidence",
        "",
        f"- Generated at: {payload.get('generated_at')}",
        f"- Commit: {payload.get('commit') or '-'}",
        f"- Status: {payload.get('status')}",
        "- Evidence basis: before = legacy confidence ordering reconstructed from the live payload; after = precision-ranked API ordering.",
        "- Provider mode: " + str((payload.get("provider_mode") or {}).get("mode") or "-"),
        "",
        "| Workspace | Candidates | Strong | Partial | Weak | Secondary duplicates | Top changed | Moved up | Moved down |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for workspace in payload.get("workspaces") or []:
        counts = workspace.get("tier_counts") or {}
        delta = workspace.get("ordering_delta") or {}
        lines.append(
            "| {workspace} | {candidates} | {strong} | {partial} | {weak} | {duplicates} | {changed} | {up} | {down} |".format(
                workspace=workspace.get("workspace_slug"),
                candidates=workspace.get("candidate_count", 0),
                strong=counts.get("strong", 0),
                partial=counts.get("partial", 0),
                weak=counts.get("weak", 0),
                duplicates=workspace.get("duplicate_secondary_count", 0),
                changed=delta.get("top_changed"),
                up=len(delta.get("moved_up") or []),
                down=len(delta.get("moved_down") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The API now exposes a deterministic ordering and explanation for every candidate. No candidate is automatically accepted, rejected, or deleted by this evidence collector.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect live candidate precision ordering evidence.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--workspace-slug", action="append", dest="workspace_slugs", default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()
    payload = collect_live(
        base_url=args.base_url,
        workspace_slugs=args.workspace_slugs or DEFAULT_WORKSPACES,
        generated_at=datetime.now(UTC).isoformat(),
    )
    _write_json(args.output_json, payload)
    _write_markdown(args.output_markdown, render_markdown(payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
