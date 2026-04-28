## Context

DecisionAtlas has completed the v0.3 RC baseline and the planned follow-up slices through real-repo decision value quality. Existing docs and scripts already provide hosted demo operator primitives: health check, smoke check, reset, reseed, deployment notes, and release validation. The gap is no longer raw capability; it is whether those pieces form a repeatable externally hosted preview process that an operator can run before showing the product to someone outside the local development loop.

The hosted preview must preserve the stable seeded demo as the public walkthrough. Imported real repositories, GitHub App sync, and private repository access are valid v0.3 capabilities, but they remain operator/admin lanes with provider, credential, and network dependencies. The design therefore centers on checklist, documentation, bounded reporting, and only minimal script or UI copy changes if verification reveals a real gap.

## Goals / Non-Goals

**Goals:**

- Produce a hosted preview readiness checklist that names required environment, service, data, and validation conditions.
- Record hosted preview verification evidence in a report that separates pass, blocking failure, non-blocking failure, and known limitation.
- Rehearse and document seeded demo reset/reseed recovery for a hosted preview environment.
- Provide an external walkthrough script that keeps the guided demo as the stable public lane and frames imported/platform lanes as bounded optional demonstrations.
- Keep release validation semantics clear: hosted preview checks are a post-RC confidence layer, not a replacement for `scripts/ci/pre-release.ps1`.

**Non-Goals:**

- No production SaaS hosting architecture.
- No billing, organization management, audit-log productization, or multiplayer review workflow.
- No secret vault or credential rotation system.
- No GitHub Marketplace/OAuth self-service installation flow.
- No requirement that default CI runs live hosted preview checks or live private repository imports.

## Decisions

1. Treat hosted preview as an operator checklist and evidence report, not a new runtime mode.

   The current stack already has environment and demo scripts. Introducing a new hosted runtime abstraction would add complexity without proving external demo readiness. The first hosted preview slice should make existing commands repeatable, explain prerequisites, and record observed results. Alternative considered: build a dedicated `preview` command. Rejected for this slice because it would hide the real service dependencies that operators need to understand.

2. Keep the seeded demo lane as the public walkthrough contract.

   The external preview should be reliable even when live providers, GitHub App webhooks, or private credentials are unavailable. The seeded guided demo remains the stable path for first impressions. Imported repository and platform access lanes can be shown as advanced/operator capabilities only after the checklist confirms their state. Alternative considered: make a real imported repository the main preview. Rejected because provider/network variability would weaken demo reliability.

3. Record hosted preview readiness separately from release readiness.

   The canonical release gate is deterministic and local; hosted preview checks depend on a running environment and may depend on networked services. The readiness report should reference the RC baseline but not claim a final SaaS release. Alternative considered: add hosted checks to `pre-release.ps1`. Rejected because it would make the mandatory gate dependent on external state.

4. Prefer documentation/report updates before script changes.

   Existing `scripts/demo/health-check.ps1`, `smoke-check.ps1`, `reset-demo.ps1`, and `reseed-demo.ps1` already cover the core operator actions. Implementation should only change scripts if verification shows missing arguments, unclear output, or broken behavior. Alternative considered: proactively rewrite scripts around hosted preview. Rejected to keep the slice small and reduce regression risk.

## Risks / Trade-offs

- [Risk] Hosted preview docs may imply production readiness. -> Mitigation: repeat the boundary that this is a preview, not production SaaS or SLA-backed deployment.
- [Risk] External environment cannot be validated from the local machine. -> Mitigation: record unavailable hosted checks as operator-guided known limitations with exact commands to rerun.
- [Risk] Demo reset/reseed could affect imported workspaces if misunderstood. -> Mitigation: document seeded lane scope and require explicit warning for broader cleanup.
- [Risk] Too much checklist detail slows operators. -> Mitigation: separate minimum pre-demo checklist from deeper troubleshooting notes.

## Migration Plan

- No database migration is expected.
- Existing hosted demo scripts remain the default operator entrypoints.
- Add or update docs and reports first; adjust scripts only if targeted verification finds a concrete defect.
- Rollback is limited to reverting documentation/report/checklist changes and any small script/copy adjustments made during implementation.

## Open Questions

- Whether this environment has a reachable external hosted URL to run `health-check.ps1` and `smoke-check.ps1` against, or whether the report should record local rehearsal plus hosted commands to rerun.
- Whether the final preview checklist should live inside the existing hosted operator guide or as a separate concise `hosted-preview-readiness.md`.
