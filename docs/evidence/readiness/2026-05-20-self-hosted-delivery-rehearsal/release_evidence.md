# Release Evidence

- Generated at: `2026-05-20T07:29:04.262987+00:00`
- Schema version: `1`
- Overall status: `passed`

## Required Gates

| Gate | Status | Source | Details |
| --- | --- | --- | --- |
| Canonical pre-release baseline | passed | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1 | {"reason": "explicit_status"} |
| OpenSpec strict validation | passed | openspec validate --all --strict | {"reason": "explicit_status"} |
| Offline benchmark fixture validation | passed | python scripts/ci/run_benchmark.py | {"reason": "explicit_status"} |

## Advisory Signals

| Signal | Status | Source | Details |
| --- | --- | --- | --- |
| Governance guardrail | passed | C:\Users\Max\Desktop\DecisionAtlas\.tmp\agent-guardrail.json | {"advisory_only": true, "agent_status": "continue", "diff_status": "pass", "drift_status": "clean", "summary": "Governance guardrail found no blocking or caution-level governance concerns."} |
| Targeted test summary | passed | - | {"reason": "explicit_status"} |
| Real-repo benchmark comparison | passed | C:\Users\Max\Desktop\DecisionAtlas\.tmp\real-repo-benchmark-comparison.json | {"comparison_type": "real-repo-benchmark-regression", "improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 1} |

## Missing Inputs

- None

## Warnings

- None

## Source Paths

- `governance_guardrail`: `C:\Users\Max\Desktop\DecisionAtlas\.tmp\agent-guardrail.json`
- `real_repo_benchmark_comparison`: `C:\Users\Max\Desktop\DecisionAtlas\.tmp\real-repo-benchmark-comparison.json`
