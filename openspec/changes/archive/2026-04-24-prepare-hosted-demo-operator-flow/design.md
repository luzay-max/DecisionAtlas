## Context

DecisionAtlas already documents a single-machine demo deployment and exposes basic service health endpoints. It also has a stable guided demo lane, a bounded imported real-repository lane, and a canonical local release baseline. What is still missing is an operator-facing hosted flow that says how to configure the environment, how to verify it is healthy, how to recover it when the demo workspace drifts, and how to keep the public walkthrough separate from imported real-repo operations.

This change stays intentionally narrow. It should improve hosted-demo operability without turning the product into a multi-tenant platform, changing the current architecture shape, or mixing in auth, private-repo, or GitHub App productization work.

## Goals / Non-Goals

**Goals:**
- Define one canonical hosted-demo operator path for environment setup, health checks, smoke verification, and recovery.
- Make backend-only provider and credential boundaries explicit so hosted setup does not leak secrets into browser-facing surfaces.
- Provide a bounded reset and reseed model that restores the stable guided demo lane.
- Document and script the boundary between the seeded demo workspace and imported workspaces.

**Non-Goals:**
- Introduce production-grade multi-tenant hosting, auth, or workspace scoping changes.
- Productize private repository access, GitHub App installation, or webhook flows.
- Replace the existing offline release baseline with hosted-demo checks.
- Re-architect the current `web + api + engine + postgres + redis` topology.

## Decisions

### 1. Expose a dedicated hosted-demo operator surface

The implementation should introduce a small, explicit operator surface for hosted demo management rather than expecting operators to compose ad hoc commands from README snippets.

This surface should include:
- a hosted health check that verifies the service chain and dependency reachability
- a hosted smoke check that verifies the stable guided walkthrough path
- bounded reset and reseed helpers for demo recovery

Rationale:
- The repo already has working health endpoints and smoke pieces, but they are scattered across docs and CI scripts.
- A single operator surface is easier to document, validate, and hand over.

Alternatives considered:
- Reuse only raw existing commands in docs. Rejected because it preserves hidden operator knowledge.
- Fold hosted checks into the default release gate. Rejected because hosted checks depend on environment availability and should remain operator-guided.

### 2. Keep hosted-demo checks separate from the default release baseline

Hosted-demo health and smoke checks should be documented as the canonical operator verification path for a running hosted environment, but they should not replace the existing offline release baseline.

Rationale:
- The current release baseline is intentionally stable and locally reproducible.
- Hosted validation is environment-dependent and is closer to operational confidence than branch-gate validation.

Alternatives considered:
- Make hosted-demo checks part of the default pre-release gate. Rejected because the gate would become dependent on operator infrastructure.

### 3. Treat demo/imported separation as an explicit operational boundary

The hosted operator flow should define the seeded demo workspace as the stable public walkthrough lane and imported workspaces as a separate operator-managed lane. Reset helpers should default to restoring the seeded demo lane without implicitly deleting imported workspaces.

Rationale:
- The product already distinguishes these lanes semantically, but hosted operation needs the boundary to be explicit.
- Operators need to know which environment actions are safe before a public demo and which actions affect imported-repo evidence work.

Alternatives considered:
- Use one shared workspace pool for demo and imported operations. Rejected because it makes public walkthrough state drift too easily.

### 4. Keep the environment contract documentation-first, with light script support

This change should prefer a documentation-first operator contract backed by a small set of helper scripts instead of attempting full deployment automation.

Rationale:
- The current project is still in a single-machine demo phase.
- Operator reliability improves significantly from a clear contract and thin helpers without forcing an early infrastructure abstraction.

Alternatives considered:
- Full container orchestration or one-click hosted deployment. Rejected as premature for this phase.

## Risks / Trade-offs

- [Operator scripts stay PowerShell-first] → Mitigation: align with the repository's current script conventions and document the command intent clearly so a later POSIX wrapper can be added without changing the contract.
- [Hosted docs may drift from actual scripts] → Mitigation: make the documented operator path call the canonical helper scripts rather than duplicating command sequences in many places.
- [Reset helpers may be interpreted as global cleanup tools] → Mitigation: require the default path to target the seeded demo lane and document imported-workspace cleanup as a separate explicit action.
- [Hosted checks could be confused with release gating] → Mitigation: state in docs and scripts that hosted health/smoke are operator-guided validation and not the default offline release gate.

## Migration Plan

1. Add the hosted-demo operator scripts and environment contract docs alongside the existing deployment guidance.
2. Update English and Chinese operator-facing docs to point to the same health, smoke, reset, and reseed flow.
3. Validate the hosted operator path locally against the current single-machine stack.
4. Keep the current release baseline unchanged while cross-linking it from the hosted operator guide.

Rollback is low risk: remove the new helper scripts and revert docs to the current generic deployment wording if the operator surface proves misleading.

## Open Questions

- Should the hosted helper scripts live under `scripts/ci/` for reuse with smoke tooling or under a new `scripts/demo/` area that is more clearly operator-facing?
- Should the hosted reset flow include a bounded imported-workspace cleanup helper now, or should it remain demo-workspace-only in this slice?
- Do we want one combined operator guide or a deployment guide plus a separate runbook document?
