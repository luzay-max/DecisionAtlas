## 1. Demo Recovery Contract

- [x] 1.1 Add or refine a seeded demo readiness check that reports whether `demo-workspace` has accepted decisions, candidate decisions, source refs, timeline-ready history, and drift alert state.
- [x] 1.2 Verify `scripts/demo/reset_seeded_demo.py` restores the full guided demo state after the candidate review queue has been consumed.
- [x] 1.3 Add coverage proving seeded demo reset preserves imported workspaces outside `demo-workspace`.
- [x] 1.4 Ensure reset failure output gives operator-readable guidance for when to rerun reset versus reseed.

## 2. Real-Stack Startup And Migration Hardening

- [x] 2.1 Keep default real-stack startup non-destructive for an existing `demo-workspace`.
- [x] 2.2 Add an explicit real-stack recovery option or documented command path for restoring the seeded demo lane before a walkthrough.
- [x] 2.3 Include seeded demo readiness or reset evidence in the real-stack validation path.
- [x] 2.4 Run and document the Alembic revision ID length guard as part of the targeted migration validation set.

## 3. Governance Guardrail Workflow

- [x] 3.1 Update guardrail workflow documentation to identify checkpoints before implementation, after implementation, before OpenSpec archive, and before commit.
- [x] 3.2 Ensure documentation states `continue`, `caution`, and `pause` handling, with `pause` requiring human review rather than automatic rewrites.
- [x] 3.3 Add or update validation coverage for guardrail summary behavior where relevant to checkpoint usage.
- [x] 3.4 Keep guardrail execution advisory by default and avoid wiring caution or pause into CI failure behavior.

## 4. Documentation And Validation

- [x] 4.1 Update quick start, deployment, hosted operator, and release checklist docs to distinguish non-destructive seed, reset, reseed, and readiness checks.
- [x] 4.2 Update the post-stage master plan baseline if it still references stale commit or migration status.
- [x] 4.3 Run targeted demo recovery, migration, and governance guardrail tests.
- [x] 4.4 Run `openspec validate --all --strict`.
- [x] 4.5 Run `python scripts/governance/agent_guardrail.py --summary` before final handoff and report any `caution` or `pause` evidence.
