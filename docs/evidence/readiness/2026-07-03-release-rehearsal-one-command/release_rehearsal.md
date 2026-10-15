# Release Rehearsal Evidence Bundle

- Label: `release-rehearsal-one-command`
- Generated at: `2026-07-03T01:53:43.418128+00:00`
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
| Benchmark trend | warning | .tmp/real-repo-benchmark-trend.json | {"covered_repositories": 1, "operationally_blocked": 0, "recommended_follow_up": ["Run or attach benchmark comparison rows for missing fixed-pool repositories.", "Review operator-guided repository setup status during release rehearsal."], "regressed": 0, "repositories": 5, "status": "warning"} |
| Benchmark comparison | warning | .tmp/real-repo-benchmark-comparison.json | {"covered_repositories": null, "operationally_blocked": 0, "recommended_follow_up": [], "regressed": 0, "repositories": 2, "status": "unknown"} |
| Multi-repo live diagnosis | warning | .tmp/multi-repo-live-diagnosis.json | {"blocking": 0, "pass": 0, "recommended_follow_up": ["evaluate_or_monitor_drift", "improve_accepted_decision_evidence", "probe_core_loop", "review_candidates", "review_candidates_or_ask_why", "run_agent_guardrail", "run_benchmark"], "selected_repo_ids": ["httpx", "fastapi"], "selected_repositories": 2, "status": "warning", "warning": 2} |
| Governance guardrail | pass | .tmp/agent-guardrail.json | {"handoff_summary": {"advisory_only": true, "agent_status": "continue", "diff_status": "pass", "drift_status": "clean", "human_questions": [], "recommended_next_actions": ["2.2 Run OpenSpec strict validation and governance guardrail summary.", "No governance drift signals detected. Continue normal review."], "required_tests": ["2.2 Run OpenSpec strict validation and governance guardrail summary.", "5.2 Run `openspec validate rehearse-self-hosted-delivery --type change --strict`.", "5.3 Run `openspec validate --all --strict`."]}, "status": "pass", "summary": "Governance guardrail found no blocking or caution-level governance concerns."} |
| Readiness history | warning | docs/evidence/readiness/index.json | {"entry_count": 3, "latest_entry_id": "2026-06-10-2026-06-10-real-stack-ai-browser-rehearsal", "status": "warning"} |

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
- probe_core_loop
- review_candidates
- review_candidates_or_ask_why
- run_agent_guardrail
- run_benchmark

## Warnings

- None

## Evidence Boundary

- This bundle stores compact statuses/counts only. Do not include tokens, raw private source, raw model output, or unbounded local logs.
