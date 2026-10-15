# Fresh Public Repository Import Rehearsal

- Generated at: `2026-07-15T05:12:52.342458+00:00`
- Status: `warning`
- Selection mode: `seeded_candidate_pool`
- Seed: `customer-host-trial-20260715`
- Candidate pool digest: `ede3d49b58e796c8f7c50ba1a8a605baedb8f5f6df349989a81fcc005c23aaf2`
- Selected repository: `hynek/structlog`
- Fresh import outcome: `fresh_import`
- Workspace slug: `github-hynek-structlog`
- Import job: `080a4b1d-54ca-4a47-a3f6-fbc401252808`
- Imported count: `1169`
- Core-loop status: `warning`
- Browser status: `operator_guided`
- Sparse recovery status: `skipped`
- Sparse model attempts: `0`
- Sparse recovered candidates: `0`

## Candidate Preflight

| Repository | Outcome | Classification | Workspace |
| --- | --- | --- | --- |
| python-trio/sniffio | reused_not_eligible | - | github-python-trio-sniffio |
| hynek/structlog | selected_fresh | - | - |

## Browser Evidence

- Browser verification will be recorded separately on the isolated self-hosted host rehearsal.

## Limitations

- A seeded bounded pool is random and reproducible but is not an unbounded sample of GitHub.
- GitHub and the real local stack are external runtime dependencies.
- A successful import can still yield evidence-limited decision quality.
- Evidence excludes credentials, raw private source, raw model output, and unbounded logs.

## Recommended Next Actions

- `evaluate_or_monitor_drift`
- `improve_accepted_decision_evidence`
- `probe_core_loop`
- `review_candidates`
- `review_candidates_before_accepted_baseline_claim`
- `review_candidates_or_ask_why`
- `run_agent_guardrail`
- `run_human_browser_rehearsal_for_fresh_workspace`
