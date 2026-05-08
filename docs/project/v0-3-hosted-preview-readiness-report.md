# DecisionAtlas Governed Hosted Preview Readiness Report

Date: 2026-05-07  
Change: `prepare-governed-hosted-preview`  
Baseline commit before this readiness update: `0d87fc3` (`feat: build real repository value benchmark`)  
Branch: `main`  
Validation mode: governed checklist and local command readiness; external hosted checks remain operator-guided unless hosted URLs are supplied.

## Summary

Status: ready for governed hosted-preview implementation, with external hosted environment checks still operator-guided.

The current baseline has deterministic release validation, seeded demo recovery, hosted operator scripts, governance Markdown ingest, accepted-rule review, local governance diff/drift checks, an AI-agent guardrail protocol, and real-repository value benchmark reporting. This report updates the hosted preview readiness story from generic service readiness to governed preview readiness: a stable guided public lane plus an optional governance second act.

No new production SaaS claim is made. The stable public walkthrough remains `demo-workspace`. Governance Markdown ingest, accepted rules, agent guardrails, imported repositories, GitHub App sync, private repository access, and live real-repository value reports are optional operator/admin lanes.

## Environment Assumptions

- No external hosted URL was provided in this session.
- `main` is currently ahead of `origin/main` by 2 local commits because earlier GitHub push attempts were blocked by network connectivity.
- The untracked `codex-history-repair.skill` file is intentionally not part of repository evidence.
- Local scripts under `scripts/demo`, `scripts/governance`, and `scripts/ci/run_benchmark.py` are the supported operator entrypoints.
- Default release validation remains `scripts/ci/pre-release.ps1`.
- Provider keys, GitHub tokens, webhook secrets, private repo credentials, and any hosted database credentials are backend-only and not required for default CI.

## Governed Hosted Preview Matrix

| Lane | Command / action | Observed result | Status | Known limitation | Follow-up |
| --- | --- | --- | --- | --- | --- |
| Baseline commit | `git rev-parse --short HEAD` | `0d87fc3` before stage 12 docs were applied. | pass | Local branch is ahead of origin because push is pending. | Push when network can reach GitHub. |
| Active OpenSpec state | `openspec list --json` | No active changes before stage 12 proposal; stage 12 is now active during implementation. | pass | Stage 12 must be archived after implementation. | Archive after validation. |
| Guided public lane | `demo-workspace` walkthrough | Existing docs and recovery scripts keep the stable public lane first. | pass | External hosted smoke still needs hosted URLs. | Run hosted smoke before public preview. |
| Hosted health | `scripts/demo/health-check.ps1 -WebBaseUrl <hosted> -ApiBaseUrl <hosted-api> -EngineBaseUrl <hosted-engine>` | Not run because no external hosted URLs were supplied. | known limitation | Cannot mark hosted health as passed without running hosted services. | Run with hosted URLs. |
| Hosted smoke | `scripts/demo/smoke-check.ps1 -WebBaseUrl <hosted> -ApiBaseUrl <hosted-api> -EngineBaseUrl <hosted-engine>` | Not run because no external hosted URLs were supplied. | known limitation | Cannot mark hosted smoke as passed without running hosted services. | Run with hosted URLs. |
| Seeded recovery | `reset-demo.ps1`; `reseed-demo.ps1`; `check_seeded_demo.py` | Commands are documented as scoped to `demo-workspace`. | operator-guided | Not rerun in this report because no hosted database was supplied. | Rehearse immediately before external preview when state is uncertain. |
| Governance Markdown ingest | `/governance`; API/engine governance tests | Product surface and APIs support import, pending drafts, human review, accepted rules, source excerpts, and review rationale. | operator-guided | Hosted product smoke still needs a running hosted environment. | Validate in hosted environment if governance second act is shown. |
| Agent guardrail | `python scripts/governance/agent_guardrail.py --summary` | To be rerun at stage 12 completion and recorded with any caution/pause evidence. | operator-guided | Current active change may produce advisory findings until archived. | Rerun before archive and commit. |
| Real-repo value evidence | `python scripts/ci/run_benchmark.py --live-real-repos --repo-id <id>` | Optional JSON/Markdown report support exists. | operator-guided | Requires running stack and existing imported workspaces. | Summarize or attach dated report externally; do not commit `.tmp` output. |
| Release gate separation | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` | Remains the mandatory deterministic release gate. | pass | Governed preview checks are not default CI enforcement. | Keep separation visible in docs. |

## Guardrail Status Handling

- `continue`: proceed after targeted validation and normal review.
- `caution`: proceed only if the advisory evidence is addressed or explicitly disclosed in the readiness handoff.
- `pause`: stop and ask for a human decision before presenting guardrail output as positive governed-preview evidence.

Guardrail output is advisory by default. It does not automatically rewrite code, update OpenSpec, accept governance rules, change roadmap documents, or block CI.

## Blocking Assessment

- Blocking product-code issues found: none from this documentation/readiness audit.
- Blocking documentation issues found: none after this change is implemented.
- Blocking hosted-environment issues found: unknown; no external hosted URL was available.
- Non-blocking limitations: hosted health/smoke, seeded recovery rehearsal, governance product smoke, and live real-repository value reports still require an operator-provided running environment.

## Pre-Demo Rerun Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"

powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"

python scripts\demo\check_seeded_demo.py
python scripts\governance\agent_guardrail.py --summary
```

If the seeded demo state drifted:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

Optional real-repository credibility evidence:

```powershell
python scripts\ci\run_benchmark.py --live-real-repos --repo-id browser-use
```

## Preview Decision

The repository has the documentation, report structure, and local operator commands needed to prepare a governed hosted preview. Do not claim the external hosted preview fully passed until an operator runs health and smoke checks against actual hosted URLs and records the result. Do not claim governance enforcement; the governed preview demonstrates human-reviewed governance memory and advisory guardrails.
