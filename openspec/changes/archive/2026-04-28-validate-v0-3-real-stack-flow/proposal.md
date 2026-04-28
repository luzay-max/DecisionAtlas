## Why

The v0.3 release-candidate baseline is documented and validated through the canonical pre-release gate, but the product still needs a reproducible real-stack validation record that proves the platformized flows work together outside the narrow demo smoke path. This change establishes that matrix before starting the next feature/productization work, so later GitHub App sync, private repo hardening, and hosted preview work have a stable factual baseline.

## What Changes

- Add a v0.3 real-stack validation report that records commands, observed results, pass/fail status, known limitations, and follow-up items.
- Validate the current local demo stack, real Postgres/Redis stack, public repository import path, login/scope role gates, GitHub App binding surface, private repo binding surface, and release gate.
- Classify any discovered issues as blocking, non-blocking, or known limitation instead of mixing validation findings with feature expansion.
- Keep optional live/provider-dependent checks operator-guided rather than adding them to default CI.
- Update release-facing validation expectations so the release baseline distinguishes canonical pre-release validation from the broader v0.3 real-stack confidence matrix.

## Capabilities

### New Capabilities

- `v0-3-real-stack-validation`: Defines the validation matrix and report contract for proving the v0.3 release-candidate product flows across demo, real stack, import, auth/scope, GitHub App binding, private repo binding, and release gates.

### Modified Capabilities

- `release-baseline-validation`: Clarifies that canonical pre-release validation remains the required release gate while v0.3 real-stack validation is a broader operator-recorded confidence layer.

## Impact

- Documentation: add or update `docs/project/v0-3-real-stack-validation-report.md`.
- Validation scripts/commands: may add small wrappers or documentation around existing health, smoke, real-stack, and pre-release commands if gaps are found.
- Product tests: may add focused tests only when validation exposes a regression or missing coverage in current v0.3 flows.
- OpenSpec: adds a new validation capability and updates release-baseline validation requirements.
