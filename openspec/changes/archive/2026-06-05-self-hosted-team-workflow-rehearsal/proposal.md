## Why

DecisionAtlas already has local accounts, roles, workspace membership, and import/review surfaces, but the self-hosted team product claim still needs a repeatable human-like rehearsal. This change turns the small-team workflow from an implementation checklist into executable evidence.

## What Changes

- Add a self-hosted team workflow rehearsal capability covering admin, reviewer, and viewer journeys.
- Add browser-level validation for login, account management visibility, and role-bounded product surfaces.
- Add operator documentation for running the rehearsal as part of self-hosted delivery readiness.
- Preserve the current manual-admin, token-paste, offline self-hosted direction; no SaaS billing, marketplace, SSO, or Git hosting scope is added.

## Capabilities

### New Capabilities
- `self-hosted-team-workflow-rehearsal`: Defines repeatable browser/operator evidence for small-team self-hosted account, permission, workspace, and review boundaries.

### Modified Capabilities
- None.

## Impact

- Affects Playwright/browser smoke coverage and self-hosted delivery documentation.
- May add deterministic API fixtures or smoke helpers for team account rehearsal.
- Does not change billing, hosted multi-tenancy, OAuth marketplace, or production license enforcement.
