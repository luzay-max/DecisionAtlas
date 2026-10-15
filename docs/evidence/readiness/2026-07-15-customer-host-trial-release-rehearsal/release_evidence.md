# Release Evidence

- Generated at: `2026-07-15T13:35:00+08:00`
- Schema version: `1`
- Overall status: `warning`

## Required Gates

| Gate | Status | Source | Details |
| --- | --- | --- | --- |
| Canonical pre-release baseline | passed | .tmp/customer-host-trial-targeted-tests.json | {"reason": "status=pass"} |
| OpenSpec strict validation | passed | .tmp/customer-host-trial-openspec-status.json | {"reason": "status=pass"} |
| Offline benchmark fixture validation | passed | .tmp/customer-host-trial-benchmark-fixture.json | {"reason": "status=pass"} |

## Advisory Signals

| Signal | Status | Source | Details |
| --- | --- | --- | --- |
| Governance guardrail | caution | .tmp/customer-host-trial-guardrail.json | {"advisory_only": null, "agent_status": "caution", "diff_status": null, "drift_status": null, "summary": "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."} |
| Targeted test summary | passed | .tmp/customer-host-trial-targeted-tests.json | {"reason": "status=pass"} |
| Real-repo benchmark comparison | passed | .tmp/customer-host-trial-benchmark-comparison.json | {"comparison_type": "real-repo-benchmark-regression", "improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 5, "sparse_operationally_blocked": 0, "sparse_regressed": 0} |
| Release trend comparison | passed | .tmp/trend-comparison.json | {"has_previous_baseline": false, "improved": 0, "regressed": 0, "total_comparisons": 1} |

## Missing Inputs

- None

## Warnings

- None

## Source Paths

- `canonical_pre_release`: `.tmp/customer-host-trial-targeted-tests.json`
- `governance_guardrail`: `.tmp/customer-host-trial-guardrail.json`
- `offline_benchmark_validation`: `.tmp/customer-host-trial-benchmark-fixture.json`
- `openspec_strict_validation`: `.tmp/customer-host-trial-openspec-status.json`
- `real_repo_benchmark_comparison`: `.tmp/customer-host-trial-benchmark-comparison.json`
- `targeted_tests`: `.tmp/customer-host-trial-targeted-tests.json`
- `trend_comparison`: `.tmp/trend-comparison.json`
