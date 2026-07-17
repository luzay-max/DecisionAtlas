# Hosted Operator Readiness

- Generated at: `2026-07-17T01:36:38.797143+00:00`
- Schema version: `1`
- Overall status: `operator_guided`
- Public walkthrough status: `operator_guided`
- Public walkthrough decision: `operator_review_required`

## Lane Status

| Lane | Group | Required public walkthrough | Status | Source | Details |
| --- | --- | --- | --- | --- | --- |
| Hosted web URL | core_hosted_services | True | operator_guided | scripts/demo/health-check.ps1 -WebBaseUrl <web> | {"reason": "no_status_or_source_path_provided"} |
| Hosted API URL | core_hosted_services | True | operator_guided | scripts/demo/health-check.ps1 -ApiBaseUrl <api> | {"reason": "no_status_or_source_path_provided"} |
| Hosted engine URL | core_hosted_services | True | operator_guided | scripts/demo/health-check.ps1 -EngineBaseUrl <engine> | {"reason": "no_status_or_source_path_provided"} |
| Hosted health check | core_hosted_services | True | operator_guided | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 | {"reason": "no_status_or_source_path_provided"} |
| Hosted guided-demo smoke check | public_walkthrough | True | operator_guided | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 | {"reason": "no_status_or_source_path_provided"} |
| Seeded demo readiness | public_walkthrough | True | operator_guided | python scripts/demo/check_seeded_demo.py --json | {"reason": "no_status_or_source_path_provided"} |
| Reset/reseed recovery drill | recovery | False | operator_guided | scripts/demo/reset-demo.ps1 or scripts/demo/reseed-demo.ps1 | {"reason": "no_status_or_source_path_provided"} |
| Governance guardrail | governance | False | not_provided | python scripts/governance/agent_guardrail.py --summary | {"reason": "no_status_or_source_path_provided"} |
| Release evidence bundle | release_evidence | False | non_blocking | .tmp/offline-real-v2-release-evidence.json | {"missing_inputs": [{"id": "real_repo_benchmark_comparison", "label": "Real-repo benchmark comparison", "required": false, "status": "not_provided"}, {"id": "trend_comparison", "label": "Release trend comparison", "required": false, "status": "not_provided"}], "overall_status": "warning", "warnings": []} |
| Real-repo benchmark evidence | optional_credibility | False | pass | .tmp/offline-real-v2-rehearsal.json | {"comparison_type": null, "failed": 0, "operationally_blocked": 0, "regressed": 0, "repositories": null} |

## Blockers

- None

## Missing Or Operator-Guided Inputs

- `web_hosted_url`: operator_guided (required_public=True)
- `api_hosted_url`: operator_guided (required_public=True)
- `engine_hosted_url`: operator_guided (required_public=True)
- `hosted_health_check`: operator_guided (required_public=True)
- `hosted_smoke_check`: operator_guided (required_public=True)
- `seeded_demo_readiness`: operator_guided (required_public=True)
- `recovery_drill`: operator_guided (required_public=False)
- `governance_guardrail`: not_provided (required_public=False)

## Recommended Next Actions

- Attach dated real-repo benchmark evidence only when the optional credibility lane is shown.
- Attach release evidence when using hosted readiness for release or preview handoff.
- Record whether reset/reseed recovery was rehearsed or intentionally deferred.
- Run and disclose guardrail caution or pause evidence if showing the governance lane.
- Run hosted health check against the API URL before external preview.
- Run hosted health check against the engine URL before external preview.
- Run hosted health check against the web URL before external preview.
- Run python scripts/demo/check_seeded_demo.py --json before external preview.
- Run scripts/demo/health-check.ps1 with hosted URLs.
- Run scripts/demo/smoke-check.ps1 with hosted URLs.

## Warnings

- None

## Rerun Commands

- Health: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 -WebBaseUrl <web> -ApiBaseUrl <api> -EngineBaseUrl <engine>`
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 -WebBaseUrl <web> -ApiBaseUrl <api> -EngineBaseUrl <engine>`
- Seeded readiness: `python scripts/demo/check_seeded_demo.py --json`
- Reset: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/reset-demo.ps1`
- Reseed: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/reseed-demo.ps1`
- Guardrail: `python scripts/governance/agent_guardrail.py --summary`

## Scope Notes

- Default reset/reseed recovery is scoped to demo-workspace and does not implicitly delete imported workspaces or governance history.
- Hosted readiness is operator-guided evidence for a running environment and does not replace scripts/ci/pre-release.ps1.
