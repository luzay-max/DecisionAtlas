## Why

DecisionAtlas already has public-repository benchmark evidence and self-hosted delivery materials, but commercial pilots depend on proving value against private repositories without leaking token material, source content, private issue/PR text, or customer identifiers. This change creates a bounded private-repo pilot evidence workflow so operators can record credible proof while keeping sensitive evidence local and redacted.

## What Changes

- Add a private-repository pilot evidence template for operator-local runs.
- Add a verifier that checks the template and generated evidence include required redaction, token-handling, scope, and limitation statements.
- Add sample JSON/Markdown evidence that demonstrates an `operator_guided` private-repo pilot without including private source content.
- Update pilot delivery and self-hosted commercial guidance so private-repo proof is handled through sanitized evidence rather than raw exports.
- Keep this workflow offline/local and do not add hosted secret vaults, billing, SaaS tenancy, OAuth, or automatic private-repository upload.

## Capabilities

### New Capabilities
- `private-repo-pilot-evidence`: Defines the safe evidence contract, template, verifier, and operator-local reporting expectations for private-repository pilots.

### Modified Capabilities
- `pilot-customer-delivery-kit`: Pilot materials must reference sanitized private-repo evidence when private-repo proof is part of the pilot claim.
- `self-hosted-commercial-baseline`: Commercial self-hosted readiness must distinguish private-repo evidence templates from actual private-repo proof and preserve operator-guided states.

## Impact

- Adds documentation under `docs/project/` for private-repo pilot evidence capture and redaction boundaries.
- Adds or extends CI/helper scripts under `scripts/ci/` to validate private-repo pilot evidence artifacts.
- Adds tests under `services/engine/tests/ci/` for the verifier.
- Updates self-hosted package/pilot verification expectations if needed so the new private-repo evidence template is included in customer-facing materials.
