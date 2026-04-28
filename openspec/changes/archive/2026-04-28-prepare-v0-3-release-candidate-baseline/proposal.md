## Why

DecisionAtlas has completed the v0.3 platform productization slices for login/scope, GitHub App installation binding, and private repository access binding. The project now needs a frozen v0.3 release-candidate baseline so future validation, hosted preview, and access-flow hardening can be judged against a stable reference point instead of a moving main branch.

## What Changes

- Prepare a `v0.3.0-rc.1` release-candidate baseline for the current branch.
- Run and record the canonical release validation result.
- Update release-facing documentation so README, quick start, deployment, FAQ, and release notes describe the same v0.3 capability boundary.
- Document current limitations clearly: no full SaaS admin console, no secret vault, no full GitHub Marketplace/OAuth installation flow, and no multi-user collaborative review workflow.
- Identify tag readiness for `v0.3.0-rc.1`.
- No product behavior changes are intended unless documentation or validation reveals a blocking mismatch.

## Capabilities

### New Capabilities
- `v0-3-release-candidate-baseline`: Defines the release-candidate contract for the v0.3 baseline, including docs, validation evidence, limitation clarity, and tag readiness.

### Modified Capabilities
- `release-baseline-validation`: Extend the release baseline contract from v0.2.2-style baseline preparation to v0.3 release-candidate preparation.
- `platform-foundation`: Clarify that the current platformized access flows are part of the v0.3 RC baseline while full SaaS productization remains out of scope.
- `hosted-demo-operator-flow`: Clarify how hosted-demo guidance relates to v0.3 RC readiness without treating hosted preview as required for the RC baseline.

## Impact

- Documentation: README, quick start, deployment, FAQ, release notes, release checklist, and project logs as needed.
- Validation: canonical `scripts/ci/pre-release.ps1` result recorded for RC readiness.
- Release process: intended tag `v0.3.0-rc.1` identified after validation passes.
- Specs/OpenSpec: new v0.3 RC baseline capability plus deltas for release validation, platform foundation, and hosted demo boundaries.
