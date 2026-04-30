## Context

The repository has completed Stage 4 via `aec6e1a Prototype governance markdown ingest`. OpenSpec active changes are currently empty, and the next product milestone should be Stage 5: Governance Diff Checker.

The master plan is a planning artifact, not runtime behavior. The change should therefore stay documentation-only and should not introduce code, database, or API changes.

## Goals / Non-Goals

**Goals:**

- Make the master plan match actual Git and OpenSpec state.
- Make the phase boundary explicit: Stage 4 complete, Stage 5 next.
- Avoid implying that accepted governance rules are already CI blockers or automatic AI verdicts.

**Non-Goals:**

- No implementation of the Stage 5 checker.
- No changes to governance ingest behavior.
- No new migration, endpoint, UI, or test fixture.

## Decisions

### Decision: Keep this as a small documentation change

The implementation only updates the master plan. This prevents a planning correction from becoming mixed with Stage 5 feature work.

### Decision: Treat Stage 5 as next, not started

The master plan should say Stage 5 is the next phase. It should not imply the checker exists until a dedicated OpenSpec change implements it.

## Validation

- Run `openspec validate record-stage-4-complete-stage-5-next --type change --strict`.
- Run `openspec validate --all --strict`.
- Use `git status` and `git log -1 --oneline` to confirm the plan reflects the actual local baseline.
