## Why

DecisionAtlas can now run from an isolated self-hosted package directory, but an operator still receives a mutable folder rather than a versioned, integrity-checkable release artifact. The next delivery milestone needs portable ZIP and tar.gz archives, checksums, an SBOM, and fail-closed verification before an external customer-host trial can rely on the handoff.

## What Changes

- Add a deterministic release-artifact publisher that wraps a verified runnable package in versioned ZIP and tar.gz archives with one stable root directory.
- Generate SHA-256 checksums, a machine-readable release manifest, and a CycloneDX JSON SBOM derived from the package lockfiles without adding a network dependency.
- Add a fail-closed artifact verifier that checks hashes, archive member parity, traversal/symlink hazards, secret/cache exclusions, SBOM structure, and the embedded package contract after extraction outside the source checkout.
- Extend the self-hosted package GitHub Actions workflow to build, verify, and upload the distributable artifacts and bounded verification evidence.
- Extend readiness evidence history so artifact publication and verification can be archived without treating an Actions artifact as customer-controlled-host proof.
- Document that cryptographic signing, air-gapped dependency caches, and customer-controlled installation remain separate follow-up capabilities.

## Capabilities

### New Capabilities

- `versioned-self-hosted-release-artifacts`: Defines versioned ZIP/tar.gz publication, checksums, SBOM, safe verification/extraction, reproducibility metadata, and independent-runner evidence boundaries.

### Modified Capabilities

- `readiness-evidence-history`: Adds versioned release-artifact publication and verification as an explicit durable evidence family with preserved warning and proof-boundary states.

## Impact

- New Python publisher/verifier scripts and deterministic unit tests under `scripts/ci/` and `services/engine/tests/ci/`.
- Updates to `.github/workflows/self-hosted-package-rehearsal.yml`, self-hosted package documentation, readiness history collection, release evidence, and delivery plans.
- No runtime API, database schema, UI, billing, multi-tenant hosting, Marketplace, OAuth, or signing-key infrastructure changes.
