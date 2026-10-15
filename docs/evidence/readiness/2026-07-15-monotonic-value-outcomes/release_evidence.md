# Release Evidence

- Generated at: `2026-07-15T14:25:00+08:00`
- Schema version: `1`
- Overall status: `passed`

## Required Gates

| Gate | Status | Source | Details |
| --- | --- | --- | --- |
| Canonical pre-release baseline | passed | .tmp/monotonic-value-outcomes-targeted-tests.json | {"reason": "status=pass"} |
| OpenSpec strict validation | passed | .tmp/monotonic-value-outcomes-openspec-status.json | {"reason": "status=pass"} |
| Offline benchmark fixture validation | passed | .tmp/monotonic-value-outcomes-fixture.json | {"reason": "status=pass"} |

## Advisory Signals

| Signal | Status | Source | Details |
| --- | --- | --- | --- |
| Governance guardrail | passed | .tmp/monotonic-value-outcomes-guardrail.json | {"advisory_only": null, "agent_status": "continue", "diff_status": null, "drift_status": null, "summary": "Governance guardrail found no blocking or caution-level governance concerns."} |
| Targeted test summary | passed | .tmp/monotonic-value-outcomes-targeted-tests.json | {"reason": "status=pass"} |
| Real-repo benchmark comparison | passed | .tmp/monotonic-value-outcomes-comparison.json | {"comparison_type": "real-repo-benchmark-regression", "improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 5, "sparse_operationally_blocked": 0, "sparse_regressed": 0} |
| Release trend comparison | passed | .tmp/monotonic-value-outcomes-trend.json | {"has_previous_baseline": false, "improved": 0, "regressed": 0, "total_comparisons": 1} |

## Missing Inputs

- None

## Warnings

- None

## Source Paths

- `canonical_pre_release`: `.tmp/monotonic-value-outcomes-targeted-tests.json`
- `governance_guardrail`: `.tmp/monotonic-value-outcomes-guardrail.json`
- `offline_benchmark_validation`: `.tmp/monotonic-value-outcomes-fixture.json`
- `openspec_strict_validation`: `.tmp/monotonic-value-outcomes-openspec-status.json`
- `real_repo_benchmark_comparison`: `.tmp/monotonic-value-outcomes-comparison.json`
- `targeted_tests`: `.tmp/monotonic-value-outcomes-targeted-tests.json`
- `trend_comparison`: `.tmp/monotonic-value-outcomes-trend.json`
