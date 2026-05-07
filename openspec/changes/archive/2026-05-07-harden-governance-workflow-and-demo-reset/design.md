## Context

DecisionAtlas already has a seeded guided demo, hosted reset/reseed scripts, real-stack startup scripts, migration tests, and an AI-agent governance guardrail. The weak point is operational reliability: a previously demonstrated `demo-workspace` can have its candidate review queue consumed, while real-stack startup currently performs non-destructive workspace seeding and therefore does not restore the full guided-demo state.

The change should harden the workflow without turning reset behavior into a surprising destructive default. Imported real-repository workspaces remain separate from the seeded guided demo lane.

## Goals / Non-Goals

**Goals:**

- Make the seeded guided demo lane recoverable to a known walkthrough state after it has been consumed or drifted.
- Preserve imported workspaces during default seeded-demo reset/reseed recovery.
- Keep real-stack startup non-destructive by default while exposing an explicit path to restore the seeded demo lane.
- Keep Alembic revision ID length validation visible in the real-stack validation path.
- Make the governance guardrail part of the local developer and AI-agent workflow before implementation, after implementation, before archive, and before commit.
- Preserve `pause` as an advisory human-review signal.

**Non-Goals:**

- Do not introduce hosted multi-tenant SaaS operations.
- Do not make governance guardrail results fail CI by default.
- Do not let agents automatically rewrite code, specs, roadmap, governance documents, or accepted rules in response to `pause`.
- Do not rebuild imported real-repository workspaces as part of seeded-demo recovery.
- Do not change public product APIs unless implementation discovers a narrow need for internal validation support.

## Decisions

### Keep real-stack startup non-destructive by default

`start-real-stack` should continue to be safe for local development by running migrations and non-destructive setup. Restoring a consumed guided-demo lane should require an explicit operator action, such as a dedicated reset/reseed command or a clearly named startup option.

Alternative considered: always reset `demo-workspace` during real-stack startup. That would make demos more predictable but would surprise operators who intentionally inspected or modified the demo state during debugging.

### Define seeded demo readiness as a state contract

The recovery flow should define what "ready for guided demo" means in terms of data state: the `demo-workspace` exists, accepted baseline decisions exist with source refs, at least one review candidate is present, the why-search path has supporting evidence, timeline history can render, and an open drift alert exists for the seeded drift lane.

Alternative considered: rely only on browser smoke tests. Browser smoke is useful, but a data-state contract catches the specific failure mode where the app starts but the review queue has already been consumed.

### Treat reset and reseed as distinct recovery depths

Reset should rebuild only the seeded demo lane and preserve imported workspaces. Reseed should first run migrations and then rebuild the seeded demo lane for cases where schema drift or database drift makes a lightweight reset insufficient.

Alternative considered: collapse both commands into one recovery command. Keeping the distinction helps operators choose the least invasive path and keeps migration-dependent behavior explicit.

### Make guardrail checkpoints explicit but advisory

The local guardrail should be documented and validated as a workflow checkpoint before implementation, after implementation, before archiving OpenSpec changes, and before committing. `continue`, `caution`, and `pause` shape agent behavior, but `pause` still requires human review rather than automatic remediation.

Alternative considered: wire the guardrail into CI or pre-commit immediately. That would skip the necessary learning period for advisory results and risks turning conservative governance signals into noisy blockers.

## Risks / Trade-offs

- Reset accidentally deletes imported workspace data -> constrain reset/reseed queries to the seeded `demo-workspace` lane and validate imported workspace preservation.
- Startup remains confusing because seed and reset sound similar -> document the difference in quick start, deployment, and operator guidance.
- Demo readiness check becomes brittle if it hard-codes too much copy -> validate stable structural expectations such as counts, review states, source refs, and drift presence rather than every display string.
- Guardrail workflow feels like ceremony -> keep commands concise and make recommended next actions visible, especially for `caution` and `pause`.
- Advisory guardrail is ignored -> document when it must be run and require its summary in stage/archive/release evidence without making it a CI blocker.
