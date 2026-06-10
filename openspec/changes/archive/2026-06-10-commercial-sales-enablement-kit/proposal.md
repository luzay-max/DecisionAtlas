## Why

The commercialization plan calls for a sales page draft, one-page product brief, and three concrete use cases so the self-hosted product can be explained before a paid pilot. Current pilot materials cover delivery mechanics, but not a compact buyer-facing narrative that can be packaged and verified.

## What Changes

- Add customer-facing sales enablement materials:
  - sales page draft
  - one-page product brief
  - three use-case briefs
- Extend pilot delivery kit verification so these materials are required and checked for commercial boundaries.
- Include sales enablement materials in the self-hosted package manifest and offline package verification.
- Keep the scope to self-hosted/private deployment positioning; no billing, marketplace, managed SaaS, or runtime license enforcement.

## Capabilities

### New Capabilities
- `commercial-sales-enablement-kit`: Customer-facing sales enablement materials and verification requirements for self-hosted pilots.

### Modified Capabilities
- `pilot-customer-delivery-kit`: Pilot kit must include or reference sales enablement materials for external evaluation.
- `offline-self-hosted-release-package`: Self-hosted package must include the sales enablement materials and verifier coverage.

## Impact

- Adds new docs under `docs/project/`.
- Updates `scripts/ci/verify_pilot_customer_delivery_kit.py`.
- Updates `scripts/ci/build_self_hosted_package.py` and `scripts/ci/verify_self_hosted_package.py`.
- Adds/updates pytest coverage for package and pilot kit verification.
