## Why

DecisionAtlas Team Self-hosted is now close to a sellable self-hosted package, but customers still need a clear commercial boundary: what is free to evaluate, what is paid, what support includes, and what remains explicitly out of scope. Without this, delivery artifacts can run, but sales/support conversations remain ambiguous.

## What Changes

- Add a self-hosted license and support boundary capability for Community, Team, and Enterprise packaging.
- Add customer-readable license/support documentation suitable for offline handoff.
- Add package manifest and verifier expectations so authorization/support boundary evidence is visible in self-hosted delivery.
- Preserve the decision to avoid strong runtime license enforcement in this stage.
- Update handoff/package docs so pilots and paid deployments have clear limitation and support terms.

## Capabilities

### New Capabilities

- `self-hosted-license-and-support-boundary`: Defines offline/self-hosted license tiers, support scope, renewal/upgrade expectations, and non-enforced evaluation boundaries.

### Modified Capabilities

- `offline-self-hosted-release-package`: Package manifest and docs include license/support boundary artifacts.
- `team-handoff-reporting`: Handoff reports can reference license/support boundary status without exposing customer secrets.

## Impact

- Adds customer-facing license/support boundary docs and templates.
- Updates package builder/verifier to include and check license/support docs.
- Updates handoff report generation to summarize license/support status when provided.
- Adds tests for package inclusion, verifier lanes, and handoff report support-boundary evidence.
