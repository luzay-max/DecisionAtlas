## Why

The real `Textualize/rich` workspace now shows 35 candidate decisions and zero accepted decisions. To improve why/drift quality without bypassing human review, operators need a controlled, auditable way to promote a small bounded set of candidate decisions into the accepted baseline.

## What Changes

- Add an operator-facing rehearsal script that inspects candidate and accepted decision counts for an imported workspace.
- Support dry-run planning by default and explicit `--confirm-accept` mutation for accepting a bounded number of candidates.
- Require bounded rationale text for accepted decisions.
- Emit JSON/Markdown evidence showing before/after baseline counts, reviewed decision IDs/titles, dry-run vs applied mode, and limitations.
- Cover the workflow with unit tests and a real `rich` local-stack rehearsal.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `real-repo-core-loop-quality`: accepted baseline gaps must have a controlled operator path for promoting selected candidates into the accepted baseline with auditable evidence.

## Impact

- New script: `scripts/ci/review_candidates_into_accepted_baseline.py`.
- New tests under `services/engine/tests/ci/`.
- Updated readiness evidence, project logs, and taskbook.
- Uses existing `/decisions` and `/decisions/{id}/review` APIs; no new API, database migration, or UI breaking change.
