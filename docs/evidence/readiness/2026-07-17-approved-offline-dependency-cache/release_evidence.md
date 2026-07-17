# Release Evidence

- Generated at: `2026-07-17T01:35:44.859621+00:00`
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
| Governance guardrail | caution | .tmp/offline-real-v2-guardrail.json | {"advisory_only": true, "agent_status": "caution", "diff_status": "pass", "drift_status": "drift_detected", "summary": "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."} |
| Targeted test summary | passed | - | {"reason": "explicit_status"} |
| Real-repo benchmark comparison | not_provided | python scripts/ci/run_benchmark.py --benchmark-compare-current <current> --benchmark-compare-baseline <baseline> --benchmark-compare-output <output> | {"reason": "no_status_or_source_path_provided"} |
| Release trend comparison | not_provided | python scripts/ci/compare_release_trends.py | {"reason": "no_status_or_source_path_provided"} |

## Missing Inputs

- `real_repo_benchmark_comparison`: not_provided (required=False)
- `trend_comparison`: not_provided (required=False)

## Warnings

- None

## Source Paths

- `governance_guardrail`: `.tmp/offline-real-v2-guardrail.json`
