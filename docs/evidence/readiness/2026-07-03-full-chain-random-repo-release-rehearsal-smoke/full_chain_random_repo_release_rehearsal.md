# Full-Chain Random Repo Release Rehearsal

- Label: `full-chain-random-repo-release-rehearsal-smoke`
- Generated at: `2026-07-03T06:35:28.000989+00:00`
- Status: `warning`
- Selected real repositories: `n8n, rich`
- Pass lanes: `1`
- Warning lanes: `4`
- Blocking lanes: `0`

## Evidence Lanes

| Lane | Status | Source | Summary |
| --- | --- | --- | --- |
| Random real GitHub repositories | warning | .tmp/multi-repo-live-diagnosis.json | {"blocking": 0, "pass": 0, "recommended_follow_up": ["evaluate_or_monitor_drift", "improve_accepted_decision_evidence", "inspect_import_quality_or_existing_decisions", "probe_core_loop", "review_candidates_or_ask_why", "run_agent_guardrail", "wait_for_import"], "selected_repo_ids": ["n8n", "rich"], "selected_repositories": 2, "status": "warning", "warning": 2} |
| Release rehearsal | warning | .tmp/release-rehearsal-evidence.json | {"generated_paths": {"multi_repo_diagnosis_json": ".tmp/multi-repo-live-diagnosis.json", "multi_repo_diagnosis_markdown": ".tmp/multi-repo-live-diagnosis.md"}, "recommended_follow_up": ["Complete or explicitly disclose operator-guided release rehearsal lanes.", "Review operator-guided repository setup status during release rehearsal.", "Review warning/blocking lanes and decide whether to rerun collectors or disclose limitations.", "Run or attach benchmark comparison rows for missing fixed-pool repositories.", "evaluate_or_monitor_drift", "improve_accepted_decision_evidence", "inspect_import_quality_or_existing_decisions", "probe_core_loop", "review_candidates_or_ask_why", "run_agent_guardrail", "wait_for_import"], "status": "warning", "summary": {"blocking": 0, "lanes": 7, "missing_lanes": 0, "operator_guided_lanes": 1, "pass": 2, "warning": 5}} |
| Customer-host v2 | warning | .tmp/external-customer-host-rehearsal-v2.json | {"host_proof_level": "customer_controlled_with_browser_smoke", "limitations": ["Replace this sample with real customer-host observations before handoff.", "Do not paste secrets, raw logs, private source, .env values, or database backups into this file."], "status": "warning", "summary": {"blocking": 0, "lanes": 7, "not_provided": 0, "operator_guided": 0, "pass": 3, "warning": 4}} |
| Browser rehearsal | pass | - | {"command": "pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line", "status": "pass", "summary": "team-self-hosted-rehearsal.spec.ts passed against local self-hosted stack"} |
| Readiness history | warning | docs/evidence/readiness/index.json | {"entry_count": 5, "latest_entry_id": "2026-07-03-external-customer-host-rehearsal-v2-smoke", "status": "warning"} |

## Limitations

- This bundle composes bounded evidence; it does not embed raw logs, secrets, or private repository content.
- Random real repository diagnosis depends on local stack, GitHub, and provider availability.
- Customer-host proof is only as strong as the supplied customer-host v2 evidence.

## Recommended Next Actions

- Review or disclose non-pass full-chain lanes: multi_repo_diagnosis, release_rehearsal, customer_host_v2, readiness_history.
- Archive this full-chain rehearsal with release/customer-host evidence before handoff.
