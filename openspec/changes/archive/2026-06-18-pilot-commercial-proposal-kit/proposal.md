## Why

DecisionAtlas already has self-hosted delivery materials, sales enablement docs, private-repo evidence templates, and customer-readable audit reports, but it still lacks the concrete commercial proposal package needed to ask for a paid pilot. The next gap is turning technical readiness into a bounded offer with pricing assumptions, acceptance criteria, support boundaries, and renewal/upgrade paths without pretending to have SaaS billing or runtime license enforcement.

## What Changes

- Add a pilot commercial proposal kit with customer-ready proposal, quote, acceptance checklist, support boundary, renewal/upgrade path, and handoff evidence requirements.
- Add a verifier that checks the commercial proposal kit exists, references the right evidence families, and preserves deferred capabilities as explicit limitations.
- Update self-hosted commercial baseline requirements so paid pilot claims must reference the proposal kit and avoid treating draft pricing as implemented billing.
- Update pilot customer delivery kit requirements so customer delivery materials can point to a commercial proposal package when the conversation moves from evaluation to paid pilot.
- Update offline self-hosted package requirements so a customer-facing package can include or reference proposal materials without embedding customer-specific secrets, payment data, or private terms.

## Capabilities

### New Capabilities
- `pilot-commercial-proposal-kit`: Defines bounded paid-pilot proposal, quote, acceptance, support, renewal, upgrade, and verification materials for self-hosted commercial handoff.

### Modified Capabilities
- `self-hosted-commercial-baseline`: Paid pilot and commercial claims must reference proposal materials and keep billing/SaaS/license-enforcement limitations visible.
- `pilot-customer-delivery-kit`: Pilot delivery materials must distinguish evaluation handoff from paid proposal handoff and link to proposal materials when needed.
- `offline-self-hosted-release-package`: Self-hosted packages must include or reference proposal-kit materials while excluding customer-specific private terms and payment data.

## Impact

- Affected docs: new proposal/quote/checklist/support/renewal docs under `docs/project/`; updates to existing self-hosted, pilot delivery, and package guides.
- Affected scripts: new proposal-kit verifier and package build/verification allowlists.
- Affected tests: new CI tests for verifier behavior and package inclusion expectations.
- No runtime billing, online license server, Marketplace, hosted multi-tenancy, or self-service OAuth will be added in this change.
