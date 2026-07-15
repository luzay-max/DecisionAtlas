# Release Evidence

- Generated at: `2026-07-15T04:30:06.873144+00:00`
- Schema version: `1`
- Overall status: `warning`

## Required Gates

| Gate | Status | Source | Details |
| --- | --- | --- | --- |
| Canonical pre-release baseline | passed | powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1 | {"reason": "explicit_status"} |
| OpenSpec strict validation | passed | openspec validate --all --strict | {"reason": "explicit_status"} |
| Offline benchmark fixture validation | passed | python scripts/ci/run_benchmark.py | {"reason": "explicit_status"} |

## Advisory Signals

| Signal | Status | Source | Details |
| --- | --- | --- | --- |
| Governance guardrail | caution | .tmp/benchmark-sparse-conversion-trends/guardrail-agent.json | {"advisory_only": null, "agent_status": "caution", "diff_status": null, "drift_status": null, "summary": "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."} |
| Targeted test summary | passed | - | {"reason": "explicit_status"} |
| Real-repo benchmark comparison | passed | .tmp/benchmark-sparse-conversion-trends/live-comparison.json | {"comparison_type": "real-repo-benchmark-regression", "improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 0, "sparse_operationally_blocked": 0, "sparse_regressed": 0} |
| Release trend comparison | not_provided | python scripts/ci/compare_release_trends.py | {"reason": "no_status_or_source_path_provided"} |

## Missing Inputs

- `trend_comparison`: not_provided (required=False)

## Warnings

- None

## Source Paths

- `governance_guardrail`: `.tmp/benchmark-sparse-conversion-trends/guardrail-agent.json`
- `real_repo_benchmark_comparison`: `.tmp/benchmark-sparse-conversion-trends/live-comparison.json`
