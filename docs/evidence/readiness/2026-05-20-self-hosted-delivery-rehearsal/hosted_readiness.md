# Hosted Operator Readiness

- Generated at: `2026-05-20T07:29:04.263530+00:00`
- Schema version: `1`
- Overall status: `pass`
- Public walkthrough status: `pass`
- Public walkthrough decision: `proceed`

## Lane Status

| Lane | Group | Required public walkthrough | Status | Source | Details |
| --- | --- | --- | --- | --- | --- |
| Hosted web URL | core_hosted_services | True | pass | scripts/demo/health-check.ps1 -WebBaseUrl <web> | {"reason": "explicit_status"} |
| Hosted API URL | core_hosted_services | True | pass | scripts/demo/health-check.ps1 -ApiBaseUrl <api> | {"reason": "explicit_status"} |
| Hosted engine URL | core_hosted_services | True | pass | scripts/demo/health-check.ps1 -EngineBaseUrl <engine> | {"reason": "explicit_status"} |
| Hosted health check | core_hosted_services | True | pass | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/health-check.ps1 | {"reason": "explicit_status"} |
| Hosted guided-demo smoke check | public_walkthrough | True | pass | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/demo/smoke-check.ps1 | {"reason": "explicit_status"} |
| Seeded demo readiness | public_walkthrough | True | pass | C:\Users\Max\Desktop\DecisionAtlas\.tmp\seeded-demo-readiness.json | {"reason": "ready=True", "summary": "Seeded demo lane is walkthrough-ready."} |
| Reset/reseed recovery drill | recovery | False | operator_guided | scripts/demo/reset-demo.ps1 or scripts/demo/reseed-demo.ps1 | {"reason": "explicit_status"} |
| Governance guardrail | governance | False | pass | C:\Users\Max\Desktop\DecisionAtlas\.tmp\agent-guardrail.json | {"agent_status": "continue", "handoff_summary": {"advisory_only": true, "agent_status": "continue", "diff_status": "pass", "drift_status": "clean", "human_questions": [], "recommended_next_actions": ["2.2 Run OpenSpec strict validation and governance guardrail summary.", "No governance drift signals detected. Continue normal review."], "required_tests": ["2.2 Run OpenSpec strict validation and governance guardrail summary.", "5.2 Run `openspec validate rehearse-self-hosted-delivery --type change --strict`.", "5.3 Run `openspec validate --all --strict`."]}, "summary": "Governance guardrail found no blocking or caution-level governance concerns."} |
| Release evidence bundle | release_evidence | False | non_blocking | C:\Users\Max\Desktop\DecisionAtlas\.tmp\release-evidence.json | {"missing_inputs": [{"id": "targeted_tests", "label": "Targeted test summary", "required": false, "status": "not_provided"}], "overall_status": "warning", "warnings": []} |
| Real-repo benchmark evidence | optional_credibility | False | pass | C:\Users\Max\Desktop\DecisionAtlas\.tmp\real-repo-benchmark-comparison.json | {"comparison_type": "real-repo-benchmark-regression", "failed": 0, "operationally_blocked": 0, "regressed": 0, "repositories": 1} |

## Blockers

- None

## Missing Or Operator-Guided Inputs

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
