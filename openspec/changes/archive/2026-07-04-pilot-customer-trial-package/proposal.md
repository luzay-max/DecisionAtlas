## Why

DecisionAtlas already has pilot delivery documents, commercial materials, and evidence collectors, but a real external trial still requires operators to manually assemble what to send, what to run, and what evidence is missing. The next step is a generated pilot trial package that turns existing materials and readiness evidence into a bounded handoff bundle for a customer/operator trial.

## What Changes

- Add a pilot customer trial package collector that generates JSON/Markdown evidence and a customer/operator-readable bundle directory.
- Include trial README, operator checklist, evidence manifest, required material links, required command list, source evidence statuses, and explicit non-clean/missing lanes.
- Preserve `operator_guided`, `not_provided`, `warning`, and `blocking` states instead of implying customer readiness.
- Reference real external host trial evidence, full-chain random repo release evidence, customer-host v2, release rehearsal, package verification, pilot kit verification, commercial proposal verification, and private-repo evidence verification.
- Add tests and smoke evidence for current local/sample state.

## Capabilities

### New Capabilities
- `pilot-customer-trial-package`: Generates a bounded pilot trial handoff bundle from existing customer-facing materials and evidence artifacts.

### Modified Capabilities
- `pilot-customer-delivery-kit`: Adds the requirement that the delivery kit can be assembled into a generated trial package before external evaluation.
- `project-completion-taskbook`: Tracks pilot customer trial package status and the remaining real external/customer-machine boundary.

## Impact

- Affected code: `scripts/ci/`, `services/engine/tests/ci/`.
- Affected docs: `docs/project/`, `docs/plans/`, OpenSpec specs.
- Affected generated artifacts: `.tmp/pilot-customer-trial-package.json`, `.tmp/pilot-customer-trial-package.md`, `.tmp/pilot-customer-trial-package/<label>/`.
- No new external dependencies and no runtime API changes.
