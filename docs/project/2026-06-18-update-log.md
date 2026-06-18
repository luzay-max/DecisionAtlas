# 2026-06-18 Update Log

## Backup Restore Upgrade Rehearsal

- Resumed OpenSpec change `backup-restore-upgrade-rehearsal` after the earlier 2026-06-10 interrupted browser-preview step.
- Added non-destructive continuity evidence support:
  - `scripts/ci/rehearse_backup_restore_upgrade.py`
  - `templates/backup-restore-upgrade-rehearsal.example.json`
  - `docs/project/backup-restore-upgrade-rehearsal.md`
- Updated self-hosted delivery and commercial materials:
  - `docs/project/self-hosted-operations-runbook.md`
  - `docs/project/self-hosted-delivery-rehearsal.md`
  - `docs/project/self-hosted-commercial-baseline.md`
- Updated package build/verification expectations:
  - `scripts/ci/build_self_hosted_package.py`
  - `scripts/ci/verify_self_hosted_package.py`
  - `services/engine/tests/ci/test_self_hosted_package.py`
- Added regression tests:
  - `services/engine/tests/ci/test_backup_restore_upgrade_rehearsal.py`

## Generated Evidence

- Backup/restore/upgrade rehearsal:
  - JSON: `.tmp/backup-restore-upgrade-rehearsal.json`
  - Markdown: `.tmp/backup-restore-upgrade-rehearsal.md`
  - Status: `operator_guided`
  - Blockers: `[]`
- Self-hosted continuity package:
  - Manifest: `.tmp/backup-restore-package-manifest.json`
  - Package verification JSON: `.tmp/backup-restore-package-verification.json`
  - Package verification Markdown: `.tmp/backup-restore-package-verification.md`
  - Status: `pass`
- Real stack health:
  - Command: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks`
  - Web: `http://127.0.0.1:3000` returned `200`
  - API: `http://127.0.0.1:3001/health` returned `200 {"ok":true}`
  - Engine: `http://127.0.0.1:8000/health` returned `200 {"ok":true}`
- Browser/Chromium readability:
  - Evidence: `.tmp/backup-restore-upgrade-rehearsal-browser-review.json`
  - Screenshot: `.tmp/backup-restore-upgrade-rehearsal-browser.png`
  - Confirmed title, non-destructive notice, `operator_guided` status, custody note, and lane status counts are visible.
- Real stack browser check:
  - Evidence: `.tmp/backup-restore-real-stack-browser.json`
  - Screenshot: `.tmp/backup-restore-real-stack-web.png`
  - Confirmed `DecisionAtlas` title, non-empty body text, and homepage navigation links.
- Public GitHub stand-in:
  - Evidence: `.tmp/backup-restore-public-github-standin.json`, `.tmp/backup-restore-public-github-standin.md`
  - Repository: `fastapi/fastapi`
  - Outcome: `reused`
  - Benchmark ready: `true`
  - Latest successful import: `2543` artifacts, `8` reviewable decisions, `13` screened-in artifacts.
  - Limitation: this is public-repo proof only and must not be presented as private-repo proof.
- Benchmark comparison:
  - Evidence: `.tmp/backup-restore-benchmark-comparison.json`, `.tmp/backup-restore-benchmark-comparison.md`
  - Current report: `.tmp/backup-restore-benchmark-comparison-current-report.json`, `.tmp/backup-restore-benchmark-comparison-current-report.md`
  - Repository: `fastapi/fastapi`
  - Status: `pass`
  - Outcome: `review_ready`
  - Drift state: `review_required`
- Governance guardrail:
  - JSON: `.tmp/backup-restore-guardrail.json`
  - Summary: `.tmp/backup-restore-guardrail-summary.txt`
  - Status: `pause`
  - Diff check: `blocked`
  - Drift report: `drift_detected`
  - Reason: the change had already been archived, so the guardrail no longer saw an active OpenSpec change for modified implementation paths.
  - Context evidence: `openspec/changes/archive/2026-06-18-backup-restore-upgrade-rehearsal/`

## Validation

- `python -m uv run pytest tests\ci\test_backup_restore_upgrade_rehearsal.py tests\ci\test_self_hosted_package.py -q`: `8 passed`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks`: passed
- `python scripts\ci\rehearse_public_github_import.py --repo-id fastapi --base-url http://127.0.0.1:3001 --wait --timeout-seconds 90 --poll-seconds 5 --output-json .tmp\backup-restore-public-github-standin.json --output-markdown .tmp\backup-restore-public-github-standin.md`: `reused`, `benchmark_ready=true`
- `python scripts\ci\rehearse_real_repo_benchmark_coverage.py --label backup-restore-rehearsal-live-fastapi --generated-at 2026-06-18T00:00:00+00:00 --live --base-url http://127.0.0.1:3001 --repo-id fastapi --output-json .tmp\backup-restore-benchmark-comparison.json --output-markdown .tmp\backup-restore-benchmark-comparison.md`: `pass`
- `pnpm exec playwright screenshot --full-page http://127.0.0.1:3000 .tmp\backup-restore-real-stack-web.png`: passed
- `openspec validate backup-restore-upgrade-rehearsal --type change --strict`: valid
- `openspec validate --all --strict`: `63 passed, 0 failed`
- Archive path: `openspec/changes/archive/2026-06-18-backup-restore-upgrade-rehearsal/`

## Boundary

- The rehearsal is intentionally non-destructive. It does not run `pg_dump`, restore PostgreSQL, apply migrations, upgrade services, or perform rollback.
- Clean continuity claims still require real backup/restore/upgrade evidence generated on the operator-controlled or customer-controlled host.
- `.tmp` evidence is scratch evidence unless reviewed and archived into readiness history.
