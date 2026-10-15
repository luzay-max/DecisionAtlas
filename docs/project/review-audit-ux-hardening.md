# Review Audit UX Hardening

Date: 2026-07-03

## What changed

The review page now shows a compact role and audit context panel near the decision review workflow.

It makes the collaboration boundary explicit:

- Reviewers and admins see that review actions are available.
- Viewers see a read-only explanation before they reach the review list.
- Recent review context is visible as bounded handoff evidence.
- Empty review history explains the next action instead of implying history exists.

## Interaction flow

```text
Team admin
  -> creates account
  -> grants workspace membership
  -> member opens review page
      -> role panel explains current permission
      -> audit panel shows recent bounded context or empty-state guidance
      -> reviewer can act
      -> viewer can read but cannot accept/reject/supersede
```

## Evidence boundary

This hardening focuses on the review interaction and workspace role affordance. It does not claim a full GitLab-style organization system, billing, marketplace distribution, or hosted multi-tenant operations.

Audit trail display currently uses bounded page-level decision context for the review screen. Backend persisted audit history remains covered by the broader collaborative review audit trail capability and can be deepened in a later change if customers need richer per-action history.

## Validation

- `pnpm --filter @decisionatlas/web test -- --run tests/review-page.test.tsx tests/review-audit-panel.test.tsx`
- `python -m pytest tests/api/test_team_api.py tests/api/test_decisions_api.py -q` from `services/engine`
- `PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`

