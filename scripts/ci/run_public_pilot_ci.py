"""Run a bounded, real-public-GitHub import in an isolated Actions runner.

This does not grade the quality of AI decisions. It uses FakeProvider and never
persists or uploads the ephemeral GitHub Actions token or the SQLite database.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "services" / "engine"
OUTPUT = ROOT / ".tmp" / "pilot-pallets-click"
REPO = "pallets/click"
BASE_URL = "http://127.0.0.1:8000"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def github_head() -> str | None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DecisionAtlas-Public-Pilot"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = Request("https://api.github.com/repos/pallets/click/commits/main", headers=headers)
        with urlopen(req, timeout=20) as response:
            sha = json.load(response).get("sha")
        return sha if isinstance(sha, str) and len(sha) == 40 else None
    except (OSError, ValueError, KeyError):
        return None


def table_counts(db_path: Path) -> dict:
    """Expose counts and limited review pointers; never export raw source or DB."""
    if not db_path.exists():
        return {}
    with sqlite3.connect(str(db_path)) as db:
        row = db.execute(
            "SELECT id FROM workspaces WHERE repo_identity = ? OR repo_url = ?",
            (REPO, f"https://github.com/{REPO}"),
        ).fetchone()
        if row is None:
            return {}
        workspace_id = row[0]
        artifacts = db.execute(
            "SELECT COUNT(*) FROM artifacts WHERE workspace_id = ?", (workspace_id,)
        ).fetchone()[0]
        decisions = db.execute(
            "SELECT review_state, COUNT(*) FROM decisions WHERE workspace_id = ? "
            "GROUP BY review_state", (workspace_id,)
        ).fetchall()
        refs = db.execute(
            "SELECT COUNT(*) FROM source_refs AS s JOIN decisions AS d ON s.decision_id = d.id "
            "WHERE d.workspace_id = ?", (workspace_id,)
        ).fetchone()[0]
        sample = db.execute(
            "SELECT d.id, d.title, d.review_state, COUNT(s.id) AS citations "
            "FROM decisions AS d LEFT JOIN source_refs AS s ON d.id = s.decision_id "
            "WHERE d.workspace_id = ? GROUP BY d.id ORDER BY d.id LIMIT 20",
            (workspace_id,),
        ).fetchall()
        evidence_rows = db.execute(
            "SELECT d.id, d.problem, d.chosen_option, s.url, a.url "
            "FROM decisions AS d LEFT JOIN source_refs AS s ON s.decision_id = d.id "
            "LEFT JOIN artifacts AS a ON a.id = s.artifact_id "
            "WHERE d.workspace_id = ? ORDER BY d.id, s.id LIMIT 100",
            (workspace_id,),
        ).fetchall()
        evidence: dict[int, dict] = {}
        for ident, problem, chosen, source_url, artifact_url in evidence_rows:
            if ident not in evidence:
                evidence[ident] = {
                    "problem": (problem or "")[:350],
                    "chosen_option": (chosen or "")[:350],
                    "source_urls": [],
                }
            # This workflow only ingests the public pallets/click repository.
            # Do not propagate untrusted external URLs, raw issue text or DB dumps.
            url = source_url or artifact_url
            if (
                isinstance(url, str)
                and url.startswith("https://github.com/pallets/click/")
                and url not in evidence[ident]["source_urls"]
                and len(evidence[ident]["source_urls"]) < 4
            ):
                evidence[ident]["source_urls"].append(url.split("?")[0][:500])
        return {
            "review_evidence": evidence,
            "artifact_count": artifacts,
            "decision_count": sum(count for _, count in decisions),
            "decisions_by_review_state": {str(state): count for state, count in decisions},
            "source_reference_count": refs,
            "candidate_preview": [
                {"id": ident, "title": title, "review_state": state, "source_ref_count": citations}
                for ident, title, state, citations in sample
            ],
        }


def write_human_review_packet(report: dict) -> None:
    """Generate an ungraded, evidence-linked worksheet for a human reviewer."""
    metrics = report.get("metrics") or {}
    evidence = metrics.get("review_evidence") or {}
    review_rows = []
    for item in metrics.get("candidate_preview") or []:
        detail = evidence.get(item["id"]) or evidence.get(str(item["id"])) or {}
        review_rows.append({
            "decision_id": item["id"],
            "title": item["title"],
            "problem": detail.get("problem", ""),
            "chosen_option": detail.get("chosen_option", ""),
            "source_urls": detail.get("source_urls", []),
            "is_real_decision": None,
            "source_verified": None,
            "review_notes": "",
        })
    packet = {
        "repository": REPO,
        "provider_mode": "fake",
        "quality_claim": "not_evaluated",
        "provenance": "real GitHub sources, deterministic FakeProvider candidates",
        "reviewed_by_human": False,
        "decision_sample_size": len(review_rows),
        "decisions": review_rows,
    }
    write_json(OUTPUT / "pilot-pallets-click-review-packet.json", packet)
    lines = [
        "# pallets/click candidate quality review — unscored",
        "",
        "**Provider: FakeProvider. This worksheet cannot establish real LLM accuracy.**",
        "",
        "For each candidate, open the GitHub citations and independently check",
        "whether it represents a genuine adopted engineering decision.",
        "Do not mark the whole sample as passing until a human records decisions and notes.",
        "",
    ]
    def safe(text: str) -> str:
        return " ".join(str(text).split()).replace("|", "/")[:350]
    for row in review_rows:
        lines.extend([
            f"## Decision {row['decision_id']}: {safe(row['title'])}",
            "",
            f"- Problem: {safe(row['problem'])}",
            f"- Chosen option: {safe(row['chosen_option'])}",
            f"- Source links: {len(row['source_urls'])}",
        ])
        for url in row["source_urls"]:
            lines.append(f"  - {url}")
        lines.extend([
            "- Human decision assessment: **not_reviewed**",
            "- Human citation verification: **not_reviewed**",
            "- Notes: _pending_",
            "",
        ])
    if not review_rows:
        lines.append("No candidates were available; quality remains not_evaluated.\n")
    (OUTPUT / "pilot-pallets-click-review-packet.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def wait_for_health(proc: subprocess.Popen, timeout_seconds: int = 90) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Engine exited before health check (code {proc.returncode})")
        try:
            with urlopen(f"{BASE_URL}/health", timeout=3) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            pass
        time.sleep(2)
    raise RuntimeError("Engine did not become healthy within 90 seconds")


def write_summary(report: dict) -> None:
    status = report["status"]
    metrics = report["metrics"]
    lines = [
        "# DecisionAtlas — public repository cloud pilot",
        "",
        f"- Result: **{status}**",
        f"- Repository: [pallets/click](https://github.com/pallets/click)",
        f"- GitHub HEAD at run time: `{report.get('github_head') or 'not_provided'}`",
        "- Provider mode: **FAKE**, no live AI quality claims",
        "- Authentication: isolated loopback test bootstrap; no production deployment",
        f"- Import outcome: `{report['import_outcome']}`",
        f"- Import job status: `{report['import_job_status']}`",
        f"- Imported artifacts (in local pilot DB): **{metrics.get('artifact_count', 'not_provided')}**",
        f"- Decision rows: **{metrics.get('decision_count', 'not_provided')}**",
        f"- Citation refs: **{metrics.get('source_reference_count', 'not_provided')}**",
        "",
        "## Evidence boundary",
        "",
        "- Real public GitHub API import is attempted. This is **not** a fixture-only result.",
        "- FakeProvider is deterministic and is **not evidence that AI reasoning is accurate**.",
        "- Human candidate review: **not_run** (20 target).",
        "- Why-search answer grading: **not_run** (10 planned questions).",
        "- Drift accuracy: **not_run** (5 planned examples).",
        "- Private repository credentials: **not_used**.",
        "",
        "See `pilot-pallets-click-summary.json` and `pilot-pallets-click-import.json` in this artifact.",
    ]
    if report.get("error"):
        lines += ["", f"- Failure category: `{report['error']}`"]
    summary = "\n".join(lines) + "\n"
    write_human_review_packet(report)
    (OUTPUT / "pilot-pallets-click-summary.md").write_text(summary, encoding="utf-8")
    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as file:
            file.write(summary)


def run() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    db_path = OUTPUT / "pilot.db"
    if db_path.exists():
        db_path.unlink()

    python = ENGINE / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        raise RuntimeError("Engine venv missing; run uv sync --project services/engine first")

    env = os.environ.copy()
    env.update({
        "DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
        "APP_ENV": "test",
        "AUTH_AUTO_BOOTSTRAP_LOCAL": "true",
        "LLM_PROVIDER_MODE": "fake",
        "EMBEDDING_PROVIDER_MODE": "fake",
        "ALLOW_UNSIGNED_WEBHOOKS_LOCAL": "false",
    })
    for key in ("LLM_API_KEY", "EMBEDDING_API_KEY"):
        env.pop(key, None)

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "repository": REPO,
        "github_head": github_head(),
        "status": "blocking",
        "provider": "fake",
        "value_validation": {
            "decision_human_review": "not_run",
            "why_search_human_scoring": "not_run",
            "drift_human_scoring": "not_run",
        },
        "import_outcome": "not_run",
        "import_job_status": "not_run",
        "metrics": {},
        "error": None,
    }

    proc = None
    log_file = None
    try:
        subprocess.run([str(python), "-m", "alembic", "upgrade", "head"],
                       cwd=ENGINE, env=env, timeout=120, check=True)
        # Do not upload engine logs, DB contents, or environment variables as artifacts.
        log_file = open(OUTPUT / "engine-local.log", "w", encoding="utf-8")
        proc = subprocess.Popen(
            [str(python), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ENGINE, env=env, stdout=log_file, stderr=subprocess.STDOUT,
        )
        wait_for_health(proc)

        cmd = [
            str(python), str(ROOT / "scripts" / "ci" / "rehearse_public_github_import.py"),
            "--repo", REPO, "--base-url", BASE_URL,
            "--wait", "--timeout-seconds", "900", "--poll-seconds", "5",
            "--output-json", str(OUTPUT / "pilot-pallets-click-import.json"),
            "--output-markdown", str(OUTPUT / "pilot-pallets-click-import.md"),
        ]
        proc_run = subprocess.run(cmd, cwd=ROOT, env=env, timeout=1020, check=False)
        import_path = OUTPUT / "pilot-pallets-click-import.json"
        if not import_path.exists():
            raise RuntimeError("Import report missing; review job logs (no import proof)")
        imported = json.loads(import_path.read_text(encoding="utf-8"))
        result["import_outcome"] = imported.get("setup", {}).get("outcome", "not_provided")
        job = imported.get("import_job") or {}
        result["import_job_status"] = job.get("status", "not_provided")
        result["metrics"] = table_counts(db_path)
        if (proc_run.returncode == 0 and
                result["import_outcome"] == "created" and
                result["import_job_status"] == "succeeded" and
                result["metrics"].get("artifact_count", 0) > 0):
            result["status"] = "import_pass_only"
        else:
            result["error"] = "import_incomplete_or_no_artifacts"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result["error"] = type(error).__name__  # No raw credentials or error payloads.
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        if log_file is not None:
            log_file.close()
        write_json(OUTPUT / "pilot-pallets-click-summary.json", result)
        write_summary(result)

    return 0 if result["status"] == "import_pass_only" else 1


if __name__ == "__main__":
    raise SystemExit(run())
