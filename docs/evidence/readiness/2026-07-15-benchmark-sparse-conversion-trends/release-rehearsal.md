# Release Rehearsal Evidence Bundle

- Label: `benchmark-sparse-conversion-live-four-profile-rehearsal`
- Generated at: `2026-07-15T04:30:07.150740+00:00`
- Status: `warning`
- Pass lanes: `2`
- Warning lanes: `5`
- Blocking lanes: `0`
- Missing lanes: `1`
- Operator-guided lanes: `1`

## Evidence Lanes

| Lane | Status | Source | Summary |
| --- | --- | --- | --- |
| Release evidence | warning | .tmp/benchmark-sparse-conversion-trends/release-evidence.json | {"advisory_signal_count": 4, "missing_input_count": 1, "required_gate_count": 3, "status": "warning", "warning_count": 0} |
| Hosted/operator readiness | operator_guided | .tmp/benchmark-sparse-conversion-trends/hosted-readiness.json | {"not_provided_count": 0, "operator_guided_count": 4, "public_walkthrough_status": "operator_guided", "status": "operator_guided"} |
| Benchmark trend | pass | .tmp/benchmark-sparse-conversion-trends/live-trend.json | {"covered_repositories": 4, "operationally_blocked": 0, "recommended_follow_up": ["Fixed-pool benchmark trend evidence is clean for the supplied comparison."], "regressed": 0, "release_evidence_ready": true, "repositories": 4, "sparse_improved": 0, "sparse_not_provided": 0, "sparse_operationally_blocked": 0, "sparse_regressed": 0, "status": "pass"} |
| Benchmark comparison | pass | .tmp/benchmark-sparse-conversion-trends/live-comparison.json | {"covered_repositories": null, "operationally_blocked": 0, "recommended_follow_up": [], "regressed": 0, "release_evidence_ready": true, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 0, "sparse_operationally_blocked": 0, "sparse_regressed": 0, "status": "pass"} |
| Multi-repo live diagnosis | not_provided | - | {"reason": "source_not_provided"} |
| Governance guardrail | warning | .tmp/benchmark-sparse-conversion-trends/guardrail-agent.json | {"handoff_summary": null, "status": "warning", "summary": "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions."} |
| Readiness history | warning | docs/evidence/readiness/index.json | {"entry_count": 17, "latest_entry_id": "2026-07-15-benchmark-sparse-conversion-live-four-profile-rehearsal", "status": "warning"} |

## Missing Lanes

- `multi_repo_diagnosis`

## Operator-Guided Lanes

- `hosted_readiness`

## Recommended Follow-up

- Attach or generate missing optional release evidence lanes before claiming a clean release.
- Complete or explicitly disclose operator-guided release rehearsal lanes.
- Fixed-pool benchmark trend evidence is clean for the supplied comparison.
- Review warning/blocking lanes and decide whether to rerun collectors or disclose limitations.

## Warnings

- None

## Evidence Boundary

- This bundle stores compact statuses/counts only. Do not include tokens, raw private source, raw model output, or unbounded local logs.
