# 2026-06-08 Update Log

## Public GitHub Import Rehearsal

- Continued OpenSpec change `public-github-import-rehearsal`.
- Added `scripts/ci/rehearse_public_github_import.py` to convert a curated public GitHub repository from selected benchmark input into explicit import/reuse setup evidence.
- Added offline script tests for reused workspace, missing workspace import creation, waiting for an existing active import, local-stack failure, and operator-guided access requirements.
- Ran real local-stack rehearsal for `fastapi/fastapi`.

## Real Evidence

- Public import rehearsal output:
  - JSON: `.tmp/public-github-import-rehearsal.json`
  - Markdown: `.tmp/public-github-import-rehearsal.md`
  - Repository: `fastapi/fastapi`
  - Workspace: `github-fastapi-fastapi`
  - Setup outcome: `reused`
  - Benchmark ready: `true`
  - Import job: `8823fe6a-bd3b-4cef-b243-9c6d1fdc5c23`
  - Import status: `succeeded`
  - Imported count: `2543`

- Model-backed extraction evidence from the import job:
  - `full_extraction_requests`: `21`
  - `completed_full_extractions`: `21`
  - `screened_in_artifacts`: `13`
  - `created_candidates`: `8`
  - `salvaged_candidates`: `7`
  - `recovered_candidates`: `3`
  - `average_full_extraction_latency_ms`: `20841`

- Live real-repo benchmark output:
  - JSON: `.tmp/fastapi-live-real-repo-validation-report.json`
  - Markdown: `.tmp/fastapi-live-real-repo-validation-report.md`
  - Result: passed
  - Bounded outcome: `review_ready`
  - Value outcome: `useful_now`
  - Candidate decisions: `8`
  - Strong candidates: `1`
  - Thin candidate ratio: `0.0`
  - Follow-up categories: none

## Validation

- `python -m uv run pytest tests/ci/test_public_github_import_rehearsal.py -q`: `5 passed`
- `openspec validate public-github-import-rehearsal --type change --strict`: passed

## Notes

- An earlier benchmark attempt on 2026-06-08 failed with `operational_failure` because `127.0.0.1:3001` was not running. After the user restarted the local stack, Web/API/Engine health probes returned 200 and the benchmark passed.
- The DeepSeek cost chart showing `<¥0.01` is consistent with the import job's 21 completed model extraction requests.

## Multi Git Source Token Import

- Started OpenSpec change `multi-git-source-token-import`.
- Added provider/access-mode metadata to repository lookup and token-backed access-source responses.
- Added `/imports/git-sources/bind` as an admin-only provider-aware setup endpoint.
- Preserved implemented GitHub token setup by delegating to the existing private access binding path.
- Added bounded outcomes for recognized but not-yet-implemented sources:
  - GitLab/Gitee token setup returns `provider_unsupported` and `plan_provider_importer`.
  - Local path setup returns `local_path_unavailable` / `operator_guided` without echoing raw server paths.
- Updated the private repository access panel to show Git provider and access mode controls while keeping token material write-only.
- Synced OpenSpec main specs for `git-source-token-import`, `live-repository-analysis`, `imported-workspace-readiness-surface`, and `private-repo-access-product-flow`.

## Multi Git Source Validation

- `python -m uv run pytest tests/api/test_imports.py -q`: `20 passed`
- `pnpm --filter @decisionatlas/api test -- imports-route`: `9 passed`
- `pnpm --filter @decisionatlas/api typecheck`: passed
- `pnpm --filter @decisionatlas/web test -- private-repo-access-panel`: `6 passed`
- Browser/operator rehearsal on the running local stack:
  - Web/API health probes returned 200.
  - After expanding advanced controls, the admin setup surface rendered provider options `github`, `gitlab`, `gitee`, `local` and access modes `token`, `public`, `local_path`.
  - Initial real GitLab setup submission was blocked by a stale running Engine process returning `404 {"detail":"Not Found"}` from `/imports/git-sources/bind`.
  - After restarting the real stack, GitLab token setup returned `provider_unsupported` with `plan_provider_importer`; the submitted token was cleared and not rendered.
  - Local path setup returned `local_path_unavailable` with `configure_server_local_path_import`; the browser surface showed server-operator-guided status.

## Collaborative Review Audit Trail

- Started and implemented OpenSpec change `collaborative-review-audit-trail`.
- Added `review_audit_events` persistence and drift alert disposition metadata.
- Added bounded audit serialization with actor username, role, target type/id, action, previous state, new state, rationale, metadata, and timestamp.
- Decision review now records audit events and decision detail returns `review_history`.
- Governance rule review and lifecycle updates now record audit events and return compact `audit_history`.
- Drift alerts now support reviewer disposition states `open`, `acknowledged`, `resolved`, and `false_positive`, with `handled_by`, `handled_at`, `disposition_rationale`, and audit history.
- Fastify API gateway now proxies `POST /drift/alerts/:alertId/disposition`.
- Web surfaces now show compact review/handling history on decision detail, governance rule cards, and drift alert detail.
- Drift alert detail now exposes reviewer disposition controls with bounded rationale.
- Synced OpenSpec main specs for `collaborative-review-audit-trail`, `imported-review-decision-quality`, `governance-markdown-ingest`, and `governance-drift-detection`.

## Collaborative Review Validation

- `python -m uv run pytest tests/api/test_decisions_api.py tests/api/test_governance.py tests/api/test_drift_api.py -q`: `21 passed`
- `pnpm --filter @decisionatlas/api test -- drift-route`: `3 passed`
- `pnpm --filter @decisionatlas/api typecheck`: passed
- `pnpm --filter @decisionatlas/web test -- decision-detail governance-page drift-detail drift-page`: `14 passed`
- `pnpm --filter @decisionatlas/web typecheck`: passed
- `openspec validate collaborative-review-audit-trail --type change --strict`: passed
- Real-stack route probe after restart:
  - Web/API/Engine health probes returned 200.
  - `POST /drift/alerts/1/disposition` returned business `404 Drift alert not found`, confirming the new route was loaded instead of route-level `404 Not Found`.
- Browser/operator rehearsal with Playwright:
  - Review page was opened on `demo-workspace`.
  - Candidate decision `339` (`Add Decision Diff View`) was accepted through the UI.
  - Decision detail showed `Review history` with `local-admin decision review accepted`.
  - Drift page was opened on `demo-workspace`.
  - Drift alert for `Use Redis Cache` was resolved through the UI with rationale `Operator rehearsal: confirmed this drift alert is handled.`
  - Drift alert detail showed `Handling history` with `local-admin drift alert disposition resolved`.

## Offline Self-Hosted Release Package

- Started OpenSpec change `offline-self-hosted-release-package`.
- Added `scripts/ci/build_self_hosted_package.py` to assemble a source-tree self-hosted package directory.
- Added `scripts/ci/verify_self_hosted_package.py` to verify package structure and emit JSON/Markdown package readiness evidence.
- Added package documentation:
  - `docs/project/self-hosted-package-guide.md`
  - `docs/project/self-hosted-operations-runbook.md`
  - `templates/self-hosted.env.example`
- Updated self-hosted readiness, delivery rehearsal, commercial baseline, and deployment docs to reference package manifest and verifier evidence.
- Package manifest records package label, version label, commit, generated timestamp, included docs/scripts/templates, required services, default URLs, validation commands, support boundary, unsupported capabilities, and readiness evidence expectations.
- Package verifier preserves explicit non-pass runtime lanes:
  - `runtime_smoke`: `operator_guided`
  - `private_repository_token_validation`: `operator_guided`
  - `live_benchmark`: `not_provided`
  - `readiness_history`: `not_provided`

## Offline Package Validation

- `python -m uv run pytest tests/ci/test_self_hosted_package.py -q`: `4 passed`
- `openspec validate offline-self-hosted-release-package --type change --strict`: passed
- Built package:
  - Package directory: `.tmp/self-hosted-package/decisionatlas-self-hosted/`
  - Manifest copy: `.tmp/self-hosted-package-manifest.json`
  - Version label: `self-hosted-preview-2026-06-08`
  - Commit: `bd481c85b88adf3cf41d9f9473dae651b3f70780`
- Verified package:
  - JSON: `.tmp/self-hosted-package-verification.json`
  - Markdown: `.tmp/self-hosted-package-verification.md`
  - Status: `pass`
  - Checked files: `25`
  - Blockers: none
- Browser/operator rehearsal:
  - Opened Web at `http://127.0.0.1:3000`: loaded.
  - Opened API health at `http://127.0.0.1:3001/health`: 200.
  - Opened Engine health at `http://127.0.0.1:8000/health`: 200.
  - Opened package README from `.tmp/self-hosted-package/decisionatlas-self-hosted/README.md`.
  - Confirmed README includes startup command, package verifier command, secret warning, and deferred capability boundary.

## Team Handoff Reporting

- Started OpenSpec change `team-handoff-reporting`.
- Added `scripts/ci/collect_team_handoff_report.py` to generate bounded JSON and Markdown handoff reports for self-hosted/team delivery.
- Report inputs now cover release evidence, hosted/operator readiness, benchmark comparison, readiness evidence history, self-hosted package verification, public GitHub import rehearsal, and optional review audit history.
- Reports preserve non-clean states such as `warning`, `blocking`, `not_provided`, `operator_guided`, and `known_limitation` instead of converting them to pass.
- Added secret and private-content filtering for raw token-like values, sensitive keys, and local-only paths.
- Updated self-hosted package docs/runbook and package manifest/verifier expectations to include team handoff report evidence.

## Team Handoff Validation

- `python -m uv run pytest tests/ci/test_team_handoff_report.py tests/ci/test_self_hosted_package.py -q`: `8 passed`
- `openspec validate team-handoff-reporting --type change --strict`: passed
- Generated handoff report:
  - JSON: `.tmp/team-handoff-report.json`
  - Markdown: `.tmp/team-handoff-report.md`
  - Overall status: `warning`
  - Reason: review audit evidence was not provided and the package still preserves operator-guided/not-provided lanes.
- Random public GitHub rehearsal:
  - Repository id: `n8n`
  - Repository: `n8n-io/n8n`
  - Evidence JSON: `.tmp/team-handoff-random-public-github-import.json`
  - Setup outcome: `reused`
  - Benchmark ready: `true`
- Browser/operator rehearsal:
  - Evidence: `.tmp/team-handoff-browser-rehearsal.json`
  - Status: `pass`
  - Opened Markdown via Chromium `file:///.../.tmp/team-handoff-report.md`
  - Confirmed title, warning status, `n8n-io/n8n`, public import evidence, and limitations section are visible.

## Self-Hosted License and Support Boundary

- Started OpenSpec change `self-hosted-license-and-support-boundary`.
- Added customer/operator documentation:
  - `docs/project/self-hosted-license-and-support-boundary.md`
  - `templates/self-hosted-entitlement.example.json`
- Defined Community, Team Self-hosted, and Enterprise Self-hosted operational boundaries.
- Kept runtime license enforcement explicitly deferred; evaluation remains non-blocking.
- Updated self-hosted package, runbook, and team handoff docs to reference entitlement evidence and paid handoff boundaries.
- Updated package manifest and verifier to include license/support boundary docs and offline entitlement template.
- Updated team handoff reporting to include `license_support` evidence and disclose missing boundary evidence.

## License Boundary Validation

- `python -m uv run pytest tests/ci/test_self_hosted_package.py tests/ci/test_team_handoff_report.py -q`: `8 passed`
- `openspec validate self-hosted-license-and-support-boundary --type change --strict`: passed
- Built package:
  - Package directory: `.tmp/self-hosted-package/decisionatlas-self-hosted/`
  - Manifest: `.tmp/self-hosted-license-package-manifest.json`
  - Version label: `self-hosted-license-boundary-2026-06-09`
- Verified package:
  - JSON: `.tmp/self-hosted-license-package-verification.json`
  - Markdown: `.tmp/self-hosted-license-package-verification.md`
  - Status: `pass`
  - Checked files: `29`
  - License/support boundary lane: `operator_guided`
- Random public GitHub rehearsal:
  - Repository id: `browser-use`
  - Repository: `browser-use/browser-use`
  - Evidence JSON: `.tmp/license-boundary-random-public-github-import.json`
  - Outcome: `local_stack_failure`
  - Reason: local API stack was not available for this rehearsal; the report preserves this non-clean state instead of converting it to pass.
- Generated handoff report:
  - JSON: `.tmp/license-boundary-team-handoff-report.json`
  - Markdown: `.tmp/license-boundary-team-handoff-report.md`
  - Overall status: `warning`
  - License/support section: `pass`
  - Tier: `Team Self-hosted`
- Browser/operator rehearsal:
  - Evidence: `.tmp/license-boundary-browser-rehearsal.json`
  - Status: `pass`
  - Confirmed report title, warning status, `browser-use/browser-use`, `license_support`, `Team Self-hosted`, and `documented_non_enforced` are visible.

## Clean Self-Hosted Install Rehearsal

- Started OpenSpec change `clean-self-hosted-install-rehearsal`.
- Added `scripts/ci/rehearse_clean_self_hosted_install.py` to copy a self-hosted package into `.tmp/clean-self-hosted-install/<label>/package-copy` and generate clean install JSON/Markdown evidence.
- Clean rehearsal verifies operator handoff entry points:
  - package manifest and README
  - environment and entitlement templates
  - self-hosted package guide, operations runbook, readiness checklist, delivery rehearsal, license/support boundary, and handoff docs
  - startup launcher and package verifier scripts
- Clean rehearsal preserves non-pass evidence states such as `warning`, `blocking`, `operator_guided`, `not_provided`, `known_limitation`, and `local_stack_failure`.
- Updated package builder, package verifier, self-hosted docs, delivery rehearsal docs, and team handoff reporting to reference clean install rehearsal evidence.

## Clean Install Validation

- `python -m uv run pytest tests/ci/test_clean_self_hosted_install_rehearsal.py tests/ci/test_self_hosted_package.py tests/ci/test_team_handoff_report.py -q`: `12 passed`
- Built package:
  - Package directory: `.tmp/self-hosted-package/decisionatlas-self-hosted/`
  - Manifest: `.tmp/clean-install-package-manifest.json`
  - Version label: `clean-self-hosted-install-2026-06-09`
  - Commit: `c00f65e`
- Verified package:
  - JSON: `.tmp/clean-install-package-verification.json`
  - Markdown: `.tmp/clean-install-package-verification.md`
  - Status: `pass`
  - Checked files: `31`
  - Blockers: none
- Generated clean install rehearsal:
  - JSON: `.tmp/clean-self-hosted-install-rehearsal.json`
  - Markdown: `.tmp/clean-self-hosted-install-rehearsal.md`
  - Status: `warning`
  - Blockers: none
  - Reason: live stack probing was not requested and handoff report preserves warning state.
- Generated clean-install-aware handoff report:
  - JSON: `.tmp/clean-install-team-handoff-report.json`
  - Markdown: `.tmp/clean-install-team-handoff-report.md`
  - Overall status: `warning`
- Browser/operator rehearsal:
  - Evidence: `.tmp/clean-install-browser-review.json`
  - Status: `pass`
  - Chromium opened `.tmp/clean-self-hosted-install-rehearsal.md` and confirmed title, warning status, clean workspace checks, source evidence, live stack probes, limitations, and recommended next actions are visible.

## Pilot Customer Delivery Kit

- Started OpenSpec change `pilot-customer-delivery-kit`.
- Added customer-readable pilot materials:
  - `docs/project/pilot-customer-delivery-kit.md`
  - `docs/project/pilot-demo-script.md`
  - `docs/project/pilot-deployment-checklist.md`
  - `docs/project/pilot-customer-faq.md`
  - `docs/project/pilot-tier-comparison.md`
  - `docs/project/pilot-delivery-email-template.md`
- Added `scripts/ci/verify_pilot_customer_delivery_kit.py` to verify pilot materials and emit JSON/Markdown evidence.
- Updated self-hosted package builder and verifier to include pilot delivery kit materials and preserve the pilot kit lane.
- Updated package guide and commercial baseline to reference the pilot delivery kit for external evaluation.

## Pilot Delivery Validation

- `python -m uv run pytest tests/ci/test_pilot_customer_delivery_kit.py tests/ci/test_self_hosted_package.py -q`: `7 passed`
- Generated pilot delivery kit verification:
  - JSON: `.tmp/pilot-customer-delivery-kit-verification.json`
  - Markdown: `.tmp/pilot-customer-delivery-kit-verification.md`
  - Status: `pass`
  - Blockers: none
- Browser/operator rehearsal:
  - Evidence: `.tmp/pilot-customer-delivery-kit-browser-review.json`
  - Status: `pass`
  - Chromium opened `docs/project/pilot-customer-delivery-kit.md` and `.tmp/pilot-customer-delivery-kit-verification.md`.
  - Confirmed title, self-hosted scope, evidence references, deferred lanes, tier/material sections, and feedback/next-action sections are visible.
