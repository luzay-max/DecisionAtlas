## 1. Deterministic Artifact Publisher

- [x] 1.1 Add a release-artifact publisher that validates the source package, validates version/commit inputs, inventories files, rejects symlinks, and computes a stable package content digest.
- [x] 1.2 Create normalized ZIP and tar.gz archives with one versioned root, stable sorted members, normalized metadata, configurable source-date epoch, and identical logical contents.
- [x] 1.3 Generate deterministic `release-artifacts.json`, `SHA256SUMS`, and CycloneDX 1.6 JSON SBOM outputs with explicit signing, vulnerability, OS/container, and dependency-cache boundaries.

## 2. Fail-Closed Verification

- [x] 2.1 Add a release-artifact verifier for manifest/checksum consistency, versioned filenames, hash/size integrity, stable roots, duplicate members, traversal, absolute/backslash paths, symlinks/special files, forbidden paths, and ZIP/tar member parity.
- [x] 2.2 Extract each validated archive into an isolated temporary directory and run the existing package verifier against both extracted roots before reporting pass.
- [x] 2.3 Emit bounded JSON/Markdown verification evidence with proof level, toolchain metadata, blockers, warnings, SBOM counts, and no secrets or unnecessary absolute paths.

## 3. Workflow, History, And Documentation

- [x] 3.1 Extend readiness history collection, index, trend, and tests with an explicit versioned release-artifact evidence family that preserves independent-runner and customer-host boundaries.
- [x] 3.2 Extend the Windows package rehearsal workflow to publish and verify archives, checksums, SBOM, and bounded reports, then upload them as a retained Actions artifact without automatically creating a public GitHub Release.
- [x] 3.3 Update package, delivery, release, and operator documentation with artifact commands, checksum/SBOM interpretation, safe extraction, signing limitations, and offline-cache boundaries.

## 4. Validation And Closeout

- [x] 4.1 Add deterministic tests for repeated builds, scoped/peer pnpm dependencies, uv dependencies, tampering, unsafe paths, duplicate members, member mismatch, malformed SBOM, forbidden contents, and extracted package verification.
- [x] 4.2 Run focused tests, full engine/API/web tests, typecheck, canonical pre-release, benchmark fixture validation, guardrail, and OpenSpec strict validation.
- [x] 4.3 Build the runnable package and release bundle, choose a fresh random public GitHub repository, verify and extract the downloaded-style artifact outside the source checkout, and complete real visible Chrome/browser/computer review, Why, Drift, and Evidence navigation from the extracted package.
- [x] 4.4 Archive bounded publication/verification evidence, update the completion taskbook, dated update log, readiness history, and next-development plan without committing ZIP/tar.gz binaries.
- [ ] 4.5 Archive the OpenSpec change, commit only scoped files, push the dedicated branch, create a stacked draft PR, and run and inspect both normal CI and package rehearsal GitHub Actions on the final SHA.
