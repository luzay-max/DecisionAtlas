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

## Pilot Commercial Proposal Kit

- Added OpenSpec change `pilot-commercial-proposal-kit` to turn the self-hosted technical handoff into a bounded paid-pilot proposal path.
- Added customer-facing proposal materials:
  - `docs/project/pilot-commercial-proposal-kit.md`
  - `docs/project/pilot-paid-quote-template.md`
  - `docs/project/pilot-acceptance-checklist.md`
  - `docs/project/pilot-support-renewal-upgrade-boundary.md`
- Added proposal kit verifier and regression tests:
  - `scripts/ci/verify_pilot_commercial_proposal_kit.py`
  - `services/engine/tests/ci/test_pilot_commercial_proposal_kit.py`
- Integrated proposal kit into the self-hosted package builder, package verifier, pilot delivery kit, package guide, and commercial baseline.

## Pilot Commercial Evidence

- Proposal kit verification:
  - JSON: `.tmp/pilot-commercial-proposal-kit-verification.json`
  - Markdown: `.tmp/pilot-commercial-proposal-kit-verification.md`
  - Status: `pass`
- Self-hosted package verification:
  - Manifest: `.tmp/pilot-commercial-proposal-package-manifest.json`
  - JSON: `.tmp/pilot-commercial-proposal-package-verification.json`
  - Markdown: `.tmp/pilot-commercial-proposal-package-verification.md`
  - Status: `pass`
- Real stack health:
  - Web: `http://127.0.0.1:3000` returned `200`
  - API: `http://127.0.0.1:3001/health` returned `{"ok":true}`
  - Engine: `http://127.0.0.1:8000/health` returned `{"ok":true}`
- Browser/Chromium proposal readability:
  - Evidence: `.tmp/pilot-commercial-proposal-kit-browser-review.json`
  - Screenshot: `.tmp/pilot-commercial-proposal-kit-browser.png`
  - Status: `pass`
  - Confirmed paid pilot offer, quote assumptions, acceptance checklist, support boundary, runtime license enforcement boundary, and not-legal-contract language are visible.
- Public GitHub evidence:
  - JSON: `.tmp/pilot-commercial-proposal-public-github.json`
  - Markdown: `.tmp/pilot-commercial-proposal-public-github.md`
  - Repository: `fastapi/fastapi`
  - Outcome: `reused`
  - Latest successful import: `2543` artifacts, `8` reviewable decisions, `13` screened-in artifacts.
  - Limitation: this reused an existing successful public import; it did not trigger a fresh model-backed import.
- Live benchmark coverage:
  - JSON: `.tmp/pilot-commercial-proposal-benchmark-coverage.json`
  - Markdown: `.tmp/pilot-commercial-proposal-benchmark-coverage.md`
  - Current report: `.tmp/pilot-commercial-proposal-benchmark-current-report.json`
  - Comparison: `.tmp/pilot-commercial-proposal-benchmark-comparison.json`
  - Status: `pass`
  - Repository outcome: `review_ready`
  - Drift state: `review_required`
- Release evidence:
  - JSON: `.tmp/pilot-commercial-proposal-release-evidence.json`
  - Markdown: `.tmp/pilot-commercial-proposal-release-evidence.md`
  - Status: `warning`
  - Reason: targeted change validation passed, but canonical full pre-release was not rerun in this step and guardrail remained advisory `caution`.
- Hosted/operator readiness:
  - JSON: `.tmp/pilot-commercial-proposal-hosted-readiness.json`
  - Markdown: `.tmp/pilot-commercial-proposal-hosted-readiness.md`
  - Public walkthrough status: `operator_guided`
- Governance guardrail:
  - JSON: `.tmp/pilot-commercial-proposal-guardrail-final.json`
  - Status: `caution`
  - Diff check: `pass`
  - Drift report: `drift_detected`
  - Handling: the specific test recommendation was covered by `test_pilot_commercial_proposal_kit.py`; historical-repeat signals remain advisory and are preserved instead of being converted to pass.

## Pilot Commercial Validation

- `python -m uv run pytest tests\ci\test_pilot_commercial_proposal_kit.py tests\ci\test_self_hosted_package.py tests\ci\test_pilot_customer_delivery_kit.py -q`: `10 passed`
- `python scripts\ci\verify_pilot_commercial_proposal_kit.py --output-json .tmp\pilot-commercial-proposal-kit-verification.json --output-markdown .tmp\pilot-commercial-proposal-kit-verification.md --generated-at 2026-06-18T00:00:00+00:00`: `pass`
- `python scripts\ci\verify_self_hosted_package.py --package .tmp\self-hosted-package\decisionatlas-self-hosted --output-json .tmp\pilot-commercial-proposal-package-verification.json --output-markdown .tmp\pilot-commercial-proposal-package-verification.md`: `pass`
- `python scripts\ci\rehearse_public_github_import.py --repo-id fastapi --base-url http://127.0.0.1:3001 --wait --timeout-seconds 120 --poll-seconds 5 --output-json .tmp\pilot-commercial-proposal-public-github.json --output-markdown .tmp\pilot-commercial-proposal-public-github.md`: `reused`, `benchmark_ready=true`
- `python scripts\ci\rehearse_real_repo_benchmark_coverage.py --live --base-url http://127.0.0.1:3001 --repo-id fastapi --output-json .tmp\pilot-commercial-proposal-benchmark-coverage.json --output-markdown .tmp\pilot-commercial-proposal-benchmark-coverage.md --output-dir .tmp --artifact-prefix pilot-commercial-proposal-benchmark --generated-at 2026-06-18T00:00:00+00:00`: `pass`
- `openspec validate pilot-commercial-proposal-kit --type change --strict`: valid
- `openspec validate --all --strict`: `64 passed, 0 failed`

## Pilot Commercial Boundary

- The proposal kit is not a legal contract, invoice, payment workflow, billing implementation, customer agreement system, hosted multi-tenant SaaS feature, Marketplace/OAuth installation flow, hosted secret vault, online license server, or runtime license enforcement.
- Filled customer quote values, customer names, payment details, signed agreements, repository names, provider keys, repository tokens, and raw private source content must remain outside committed artifacts.
- Public GitHub evidence remains public-repo proof only. Private-repo pilot claims still require sanitized evidence generated on the customer-controlled host.
