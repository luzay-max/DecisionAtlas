# Release Rehearsal Evidence Bundle

- Label: `release-rehearsal-one-command`
- Generated at: `2026-07-10T09:14:39.3628310+08:00`
- Status: `warning`
- Pass lanes: `2`
- Warning lanes: `5`
- Blocking lanes: `0`
- Missing lanes: `0`
- Operator-guided lanes: `1`

## Evidence Lanes

| Lane | Status | Source | Summary |
| --- | --- | --- | --- |
| Release evidence | pass | .tmp/release-evidence.json | {"advisory_signal_count": 3, "missing_input_count": 0, "required_gate_count": 3, "status": "pass", "warning_count": 0} |
| Hosted/operator readiness | operator_guided | .tmp/hosted-operator-readiness.json | {"not_provided_count": 0, "operator_guided_count": 3, "public_walkthrough_status": "operator_guided", "status": "operator_guided"} |
| Benchmark trend | warning | .tmp/real-repo-benchmark-trend.json | {"covered_repositories": 1, "operationally_blocked": 0, "recommended_follow_up": ["Run or attach benchmark comparison rows for missing fixed-pool repositories.", "Review operator-guided repository setup status during release rehearsal."], "regressed": 0, "release_evidence_ready": true, "repositories": 5, "status": "warning"} |
| Benchmark comparison | pass | .tmp/real-repo-benchmark-comparison.json | {"covered_repositories": null, "operationally_blocked": 0, "recommended_follow_up": [], "regressed": 0, "release_evidence_ready": true, "repositories": 2, "status": "pass"} |
| Multi-repo live diagnosis | warning | .tmp/multi-repo-live-diagnosis.json | {"action_categories": {"blocking": 0, "external_dependency": 0, "not_provided": 0, "operator_setup": 0, "product_controlled": 4}, "blocking": 0, "pass": 0, "recommended_follow_up": ["evaluate_or_monitor_drift", "improve_accepted_decision_evidence", "inspect_citations", "inspect_guardrail_findings", "probe_core_loop", "review_candidates", "review_candidates_or_ask_why", "run_benchmark"], "selected_repo_ids": ["n8n", "rich"], "selected_repositories": 2, "status": "warning", "warning": 2} |
| Governance guardrail | warning | .tmp/agent-guardrail.json | {"error": "Failed to parse JSON from C:\\Users\\Max\\Desktop\\DecisionAtlas\\.tmp\\agent-guardrail.json: Expecting value: line 1 column 1 (char 0)", "reason": "source_unreadable"} |
| Readiness history | warning | docs/evidence/readiness/index.json | {"entry_count": 11, "latest_entry_id": "2026-07-08-accepted-decision-baseline-smoke", "status": "warning"} |

## Missing Lanes

- None

## Operator-Guided Lanes

- `hosted_readiness`

## Recommended Follow-up

- Complete or explicitly disclose operator-guided release rehearsal lanes.
- Review operator-guided repository setup status during release rehearsal.
- Review warning/blocking lanes and decide whether to rerun collectors or disclose limitations.
- Run or attach benchmark comparison rows for missing fixed-pool repositories.
- evaluate_or_monitor_drift
- improve_accepted_decision_evidence
- inspect_citations
- inspect_guardrail_findings
- probe_core_loop
- review_candidates
- review_candidates_or_ask_why
- run_benchmark

## Warnings

- Failed to parse JSON from C:\Users\Max\Desktop\DecisionAtlas\.tmp\agent-guardrail.json: Expecting value: line 1 column 1 (char 0)

## Evidence Boundary

- This bundle stores compact statuses/counts only. Do not include tokens, raw private source, raw model output, or unbounded local logs.
