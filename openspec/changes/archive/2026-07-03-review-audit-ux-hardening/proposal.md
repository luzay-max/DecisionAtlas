## Why

DecisionAtlas already supports team roles and review actions, but the UI still needs clearer audit guidance for small self-hosted teams. Admins, reviewers, and viewers should immediately understand what they can do, what happened, and what the next action is.

## What Changes

- Harden the review/audit UI so imported decisions show clearer review state, role boundary, and audit trail context.
- Make reviewer/viewer/admin affordances explicit without changing the authorization model.
- Add browser-level coverage for review history visibility and viewer read-only behavior.
- Add documentation and update the completion taskbook / update log.

## Capabilities

### New Capabilities
- `review-audit-ux-hardening`: Defines review/audit interaction hardening for small-team self-hosted workflows.

### Modified Capabilities
- `collaborative-review-audit-trail`: Review audit records must be surfaced in a clearer UI flow.
- `workspace-member-permissions`: Viewer/reviewer/admin UI affordances must reflect role boundaries.
- `workspace-interaction-flow`: The workspace flow must expose next actions after review and audit events.
- `project-completion-taskbook`: The taskbook moves from release rehearsal to external customer host rehearsal after this hardening.

## Impact

- Frontend components and tests in `apps/web`.
- Potential Playwright/browser test additions.
- Documentation and OpenSpec spec updates.
- No database or backend authorization changes expected unless existing API data needs safer presentation.
