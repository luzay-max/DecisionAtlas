## Why

DecisionAtlas is moving from a developer-run local product into a small-team self-hosted product. The current scripts and checklists prove the system can run, but they do not yet define a customer-deliverable offline package with install, verification, backup, restore, upgrade, and handoff evidence.

## What Changes

- Add a release-package contract for building a self-hosted handoff directory or archive.
- Add package manifest evidence so operators can see version, commit, included docs, scripts, required services, and validation commands.
- Add a package smoke/readiness verifier that checks package structure and records bounded pass/warning/operator-guided states.
- Add first-admin initialization guidance and environment template for deployment use.
- Add backup, restore, and upgrade runbook coverage to the package handoff path.
- Preserve current local development scripts; this change does not replace Docker Compose, CI, or existing real-stack startup.

## Capabilities

### New Capabilities

- `offline-self-hosted-release-package`: Defines the package layout, manifest, verification, environment template, runbooks, and evidence required before handing DecisionAtlas to a self-hosted operator.

### Modified Capabilities

- `self-hosted-delivery-rehearsal`: Requires package verification evidence as part of the Team Self-hosted handoff rehearsal.
- `self-hosted-commercial-baseline`: Clarifies that commercial self-hosted claims reference a package manifest and operator runbooks, not just source-tree development commands.

## Impact

- Adds packaging scripts under `scripts/` for assembling and verifying a self-hosted package.
- Adds or updates documentation under `docs/project/` for package layout, first-admin setup, backup/restore, and upgrade.
- Adds OpenSpec requirements and tests for package manifest and verifier output.
- Affects release evidence only as an additional package-readiness input; no runtime license enforcement, billing, SaaS tenancy, or Marketplace/OAuth work is included.
