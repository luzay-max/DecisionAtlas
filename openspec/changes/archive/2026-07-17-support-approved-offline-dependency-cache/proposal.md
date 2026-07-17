## Why

DecisionAtlas can now ship a verified runnable release artifact, but installation still depends on live npm, PyPI, Playwright, and container registries. A bounded, reproducible offline dependency bundle is required before the self-hosted package can be installed in restricted-network environments without copying arbitrary developer caches or weakening supply-chain checks.

## What Changes

- Add an online preparation command that materializes approved pnpm, uv, Playwright browser, and Docker image caches from the existing package lockfiles and runtime manifest.
- Generate a deterministic offline bundle manifest, exact SHA-256 coverage, and CycloneDX SBOM with explicit platform, toolchain, image, and proof boundaries.
- Add a fail-closed verifier for package identity, lockfile binding, category completeness, path safety, checksums, SBOM structure, container image allowlists, and secret/cache contamination.
- Add an isolated offline-consumption rehearsal that installs Node and Python dependencies with offline flags, uses only the bundled browser and container images, blocks registry access, starts Engine/API/Web, and emits bounded evidence.
- Extend package documentation, GitHub Actions, and readiness history so offline evidence is retained without committing the large cache bundle to Git.

## Capabilities

### New Capabilities

- `approved-offline-dependency-cache`: Defines the online preparation, bounded bundle contract, fail-closed verification, and offline installation/startup proof for approved dependency caches.

### Modified Capabilities

- `readiness-evidence-history`: Adds an explicit offline dependency bundle evidence family with cache category, platform, checksum, SBOM, blocker, and proof-boundary summaries.

## Impact

- Adds CI/operator scripts for preparing, verifying, and rehearsing offline bundles.
- Updates runnable package metadata, package documentation, the Windows package rehearsal workflow, and readiness history collection.
- Adds Python tests and a bounded browser shell check; large pnpm/uv/browser/container cache payloads remain generated artifacts and are never committed.
- Does not claim customer-controlled-host, cross-platform, private-repository, cryptographic-signing, vulnerability-analysis, or fully air-gapped operational proof.
