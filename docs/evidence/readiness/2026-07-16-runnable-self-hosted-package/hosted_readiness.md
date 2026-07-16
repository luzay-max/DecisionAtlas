# Hosted Operator Readiness

- Generated at: `2026-07-16T08:09:02.096257+00:00`
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
| Hosted health check | core_hosted_services | True | pass | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 | {"reason": "explicit_status"} |
| Hosted guided-demo smoke check | public_walkthrough | True | pass | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 | {"reason": "explicit_status"} |
| Seeded demo readiness | public_walkthrough | True | pass | python scripts/demo/check_seeded_demo.py --json | {"reason": "explicit_status"} |
| Reset/reseed recovery drill | recovery | False | operator_guided | scripts/demo/reset-demo.ps1 or scripts/demo/reseed-demo.ps1 | {"reason": "no_status_or_source_path_provided"} |
| Governance guardrail | governance | False | non_blocking | .tmp/agent-guardrail.json | {"agent_status": "caution", "handoff_summary": {"advisory_only": true, "agent_status": "caution", "diff_status": "pass", "drift_status": "drift_detected", "human_questions": [], "recommended_next_actions": ["3.1 Add deterministic tests for runtime inclusion, secret/cache exclusion, legacy package blocking, missing runtime assets, isolated-copy command roots, and independent-runner boundary classification.", "Review the historical issue before repeating the same implementation pattern."], "required_tests": ["3.1 Add deterministic tests for runtime inclusion, secret/cache exclusion, legacy package blocking, missing runtime assets, isolated-copy command roots, and independent-runner boundary classification.", "3.2 Run focused package tests, full engine/API/web tests, typecheck, benchmark fixture validation, guardrail, and OpenSpec strict validation.", "Run or add targeted tests for changed behavior."]}, "summary": "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."} |
| Release evidence bundle | release_evidence | False | non_blocking | .tmp/runnable-release-evidence.json | {"missing_inputs": [{"id": "trend_comparison", "label": "Release trend comparison", "required": false, "status": "not_provided"}], "overall_status": "warning", "warnings": []} |
| Real-repo benchmark evidence | optional_credibility | False | pass | .tmp/githits-live-core-loop.json | {"comparison_type": null, "failed": 0, "operationally_blocked": 0, "regressed": 0, "repositories": null} |

## Blockers

- None

## Missing Or Operator-Guided Inputs

- `web_hosted_url`: operator_guided (required_public=True)
- `api_hosted_url`: operator_guided (required_public=True)
- `engine_hosted_url`: operator_guided (required_public=True)
- `recovery_drill`: operator_guided (required_public=False)

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
