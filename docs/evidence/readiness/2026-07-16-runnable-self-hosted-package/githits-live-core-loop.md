# Imported Workspace Core Loop Rehearsal

- Generated at: `2026-07-16T07:24:26.081419+00:00`
- Status: `warning`
- Repository: `githits-com/githits-cli`
- Workspace slug: `github-githits-com-githits-cli`
- Base URL: `http://127.0.0.1:3001`
- Accepted baseline: `empty`

## Accepted Baseline

- Summary: `{"accepted_count": 0, "accepted_sample_titles": [], "candidate_count": 30, "candidate_sample_titles": ["Capability-gate code navigation feature", "Improve search match highlighting", "fix: prevent auth refresh token reuse races"], "next_action": "review_candidates_into_accepted_baseline", "status": "empty", "strength": "none"}`

## Lanes

| Lane | Status | Action category | Grounding | Summary | Next action |
| --- | --- | --- | --- | --- | --- |
| setup | pass | pass | - | Workspace setup source `explicit` reported `provided`. | probe_core_loop |
| dashboard | pass | pass | - | Dashboard summary loaded for imported workspace. | review_candidates_or_ask_why |
| review | pass | pass | - | Review queue has candidate decisions. | review_candidates |
| why_search | warning | product_controlled | {"reasons": [{"code": "missing_accepted_decision_evidence", "evidence": {"accepted_baseline_status": "empty", "accepted_decision_count": 0, "answer_status": "review_required", "citation_count": 0, "primary_decision_present": false, "workspace_mode": "imported"}, "lane": "why_search", "next_action": "improve_accepted_decision_evidence", "summary": "Why-search has no citations or primary decision to ground the answer."}]} | Why-search returned `review_required`. | improve_accepted_decision_evidence |
| drift | warning | product_controlled | {"reasons": [{"code": "missing_accepted_decision_evidence", "evidence": {"accepted_baseline_status": "empty", "accepted_decision_count": 0, "alert_count": 0, "drift_state": "review_required", "evaluation_request_status": "ok", "evaluation_state": "review_required"}, "lane": "drift", "next_action": "evaluate_or_monitor_drift", "summary": "Drift warning may be caused by insufficient accepted-decision baseline evidence."}]} | Drift lane returned `review_required` with 0 alert(s). | evaluate_or_monitor_drift |
| guardrail | warning | product_controlled | - | Guardrail returned `caution`. | inspect_guardrail_findings |

## Recommended Next Actions

- `evaluate_or_monitor_drift`
- `improve_accepted_decision_evidence`
- `inspect_guardrail_findings`
- `probe_core_loop`
- `review_candidates`
- `review_candidates_or_ask_why`

## Evidence Boundary

- This report stores compact statuses/counts only. Do not include tokens, raw private source, or raw model output.
