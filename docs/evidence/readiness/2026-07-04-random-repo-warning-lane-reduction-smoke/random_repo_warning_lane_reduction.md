# Random Repo Warning Lane Reduction

- Status: `warning`
- Label: `2026-07-04-random-repo-warning-lane-reduction-smoke`
- Generated: `2026-07-04T00:00:00+00:00`
- Selected repositories: n8n, rich

## Summary

- sources: `4`
- classified_lanes: `14`
- product_controlled: `3`
- operator_guided: `11`
- external_dependency: `0`
- not_provided: `0`
- blocking: `0`

## Reduction Actions

- `P0` `product_controlled`: Reduce product-controlled import/review/why/drift/guardrail warning lanes for n8n, rich.
- `P1` `operator_guided`: Replace template/manual host evidence with real operator observations or disclose it in release notes.

## Classified Lanes

- `operator_guided` `warning` multi_repo_diagnosis:n8n: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` multi_repo_diagnosis:rich: warning appears tied to hosted/customer/operator proof
- `product_controlled` `warning` full_chain_random_repo_release:multi_repo_diagnosis: warning appears reducible through product evidence or workflow improvements
- `operator_guided` `warning` full_chain_random_repo_release:release_rehearsal: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` full_chain_random_repo_release:customer_host_v2: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` full_chain_random_repo_release:readiness_history: warning appears tied to hosted/customer/operator proof
- `operator_guided` `operator_guided` release_rehearsal:hosted_readiness: source lane requires operator/manual proof
- `operator_guided` `warning` release_rehearsal:benchmark_trend: warning appears tied to hosted/customer/operator proof
- `product_controlled` `warning` release_rehearsal:benchmark_comparison: warning appears reducible through product evidence or workflow improvements
- `product_controlled` `warning` release_rehearsal:multi_repo_diagnosis: warning appears reducible through product evidence or workflow improvements
- `operator_guided` `warning` release_rehearsal:readiness_history: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` real_external_host_trial:placeholder_review: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` real_external_host_trial:customer_host_v2: warning appears tied to hosted/customer/operator proof
- `operator_guided` `warning` real_external_host_trial:full_chain_random_repo_release: warning appears tied to hosted/customer/operator proof

## Sources

- `multi_repo_diagnosis` `warning` .tmp/multi-repo-live-diagnosis.json
- `full_chain_random_repo_release` `warning` .tmp/full-chain-random-repo-release-rehearsal.json
- `release_rehearsal` `warning` .tmp/release-rehearsal-evidence.json
- `real_external_host_trial` `warning` .tmp/real-external-host-trial-evidence.json

## Limitations

- This reducer explains warning lanes but does not change source release evidence status.
- Classification is deterministic and based on bounded source evidence, not raw logs or private source.
- External-host and customer-host confidence depends on the supplied operator evidence.
