## Why

DecisionAtlas has hosted-preview documentation and local operator scripts, but hosted/operator delivery still depends on manual reading across several docs and does not produce one repeatable readiness artifact for an external demo. This change turns hosted preview preparation into a concrete operator runbook and evidence flow while keeping billing, multi-tenancy, Marketplace, and self-service OAuth out of scope.

## What Changes

- Add a hosted/operator delivery readiness flow that standardizes pre-demo checks, recovery drill recording, limitation disclosure, and handoff evidence.
- Provide a machine-readable and Markdown readiness record for hosted preview preparation, similar in spirit to release evidence but scoped to a running hosted/operator environment.
- Strengthen the hosted operator guide with a single pre-demo sequence, rerun commands, reset/reseed decision points, and public walkthrough stop/go rules.
- Integrate existing checks where possible: hosted health, hosted smoke, seeded demo readiness, governance guardrail, optional real-repo benchmark comparison, and release evidence bundle references.
- Keep hosted checks operator-guided by default; no default CI enforcement, no destructive cleanup, no credential collection, and no hosted SaaS management work.

## Capabilities

### New Capabilities

- `hosted-operator-delivery-readiness`: hosted/operator readiness evidence, runbook flow, stop/go classification, and handoff generation for external preview preparation.

### Modified Capabilities

- `hosted-demo-operator-flow`: clarify that hosted operator delivery readiness produces a bounded runbook and readiness artifact for external preview handoff.
- `release-evidence-automation`: allow hosted/operator readiness records to reference release evidence bundles without making hosted checks part of the canonical release gate.

## Impact

- New or updated script under `scripts/demo/` or `scripts/ci/` for collecting hosted/operator readiness evidence.
- Documentation updates in hosted operator guide, hosted preview readiness docs, and release checklist references.
- Tests for readiness classification, missing hosted URL handling, recovery evidence disclosure, and Markdown output.
- No database migration, no product API changes required, and no changes to default release gate semantics.
