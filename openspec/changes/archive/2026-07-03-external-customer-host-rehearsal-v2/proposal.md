## Why

DecisionAtlas already has local self-hosted packaging, clean install, release rehearsal, and external install evidence collectors, but customer-host proof is still fragmented. This change adds a v2 rehearsal path that turns those pieces into a repeatable customer-controlled host readiness workflow without pretending local developer evidence is the same as customer-host validation.

## What Changes

- Add a customer-host rehearsal v2 collector that can combine package verification, clean install rehearsal, external install evidence, browser smoke, release rehearsal, and readiness history into JSON/Markdown evidence.
- Add an external/customer host template so an operator can collect sanitized facts from a non-developer machine.
- Preserve `not_provided`, `operator_guided`, `warning`, and `blocking` states instead of converting missing customer evidence into pass.
- Archive the generated rehearsal evidence into readiness history when requested.
- Update the completion taskbook and update log so the next project state is driven by customer-host evidence rather than more local-only checks.

## Capabilities

### New Capabilities
- `external-customer-host-rehearsal-v2`: repeatable customer-host rehearsal evidence bundling package, install, browser, release, and readiness history signals.

### Modified Capabilities
- `external-self-hosted-install-evidence`: external install evidence can be generated from a v2 sanitized host template.
- `self-hosted-delivery-rehearsal`: delivery rehearsal can reference customer-host v2 evidence before claiming external host readiness.
- `readiness-evidence-history`: readiness history can archive customer-host v2 rehearsal bundles.
- `project-completion-taskbook`: taskbook reflects customer-host rehearsal progress and remaining product gaps.

## Impact

- Adds a CI/operator script under `scripts/ci/`.
- Adds targeted tests under `services/engine/tests/ci/`.
- Adds customer/operator documentation under `docs/project/`.
- Updates OpenSpec specs and the 2026-07-03 taskbook/update log.
- No runtime API, database, or breaking user-facing behavior changes.
