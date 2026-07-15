## Why

The self-hosted delivery path can verify package structure and local readiness, but it cannot yet produce a complete, bounded record of a real external-host trial. The next roadmap milestone is to make an operator's install, login, repository import, review, Why, Drift, recovery, and redaction observations usable as one auditable handoff without overstating local smoke evidence as customer proof.

## What Changes

- Add a versioned customer-host trial input contract covering host identity, package identity, startup and health, administrator login, account/workspace setup, repository import, review, Why, Drift, backup/recovery, and browser evidence.
- Extend the external-host evidence collector to validate these lanes, preserve non-clean states, redact external absolute paths, and distinguish a real customer-controlled host from a local or template rehearsal.
- Add an operator-facing trial checklist and a repeatable command sequence that can be executed on a clean host without automatically mutating customer infrastructure.
- Connect the trial result to readiness history and self-hosted delivery handoff evidence.
- Add focused tests plus a real isolated-host rehearsal where the environment permits it; record any missing non-local proof as `operator_guided` rather than fabricating `pass`.

## Capabilities

### New Capabilities

- `customer-host-trial-operator-kit`: Versioned input contract, operator checklist, bounded lane vocabulary, and archive-ready trial package for an external self-hosted host.

### Modified Capabilities

- `real-external-host-trial-evidence`: Require core delivery lanes and prevent external absolute paths or template inputs from becoming clean customer proof.
- `self-hosted-delivery-rehearsal`: Add the customer-host trial kit to the execution order and handoff boundary.

## Impact

- `scripts/ci/collect_real_external_host_trial_evidence.py` and related readiness-history adapters.
- New or updated sanitized template and operator documentation under `templates/` and `docs/project/`.
- Engine CI tests for input validation, status aggregation, path redaction, secret detection, and history archival.
- No new runtime dependency and no automatic installation, import, browser, database, Docker, or customer-infrastructure mutation from the collector itself.
