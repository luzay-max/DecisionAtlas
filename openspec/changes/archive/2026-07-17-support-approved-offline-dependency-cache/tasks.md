## 1. Bundle Contract And Online Preparation

- [x] 1.1 Add shared lockfile/SBOM, platform-contract, safe-path, hashing, and bounded command helpers for offline dependency evidence.
- [x] 1.2 Implement online bundle preparation for pnpm store, uv cache, Playwright Chromium, and allowlisted Compose container images with disposable environments and no developer-cache reuse.
- [x] 1.3 Generate a package-bound manifest, exact `SHA256SUMS`, CycloneDX 1.6 SBOM, category summaries, tool/image identities, and bounded JSON/Markdown preparation evidence.

## 2. Fail-Closed Verification

- [x] 2.1 Implement offline bundle verification for manifest/checksum exact coverage, path safety, symlink/special-file rejection, category completeness, platform/toolchain contract, SBOM structure, and package lockfile bindings.
- [x] 2.2 Reject tampering, unlisted or case-colliding files, forbidden content, missing dependencies, moving container references, mismatched packages, and unsupported consumer platforms before installation.
- [x] 2.3 Emit bounded verification JSON/Markdown with explicit process-enforced offline, customer-host, signing, vulnerability, and cross-platform boundaries.

## 3. Offline Consumption And Browser Proof

- [x] 3.1 Implement isolated offline consumption using pnpm/uv offline flags, blackhole registry proxies, dedicated Playwright browser path, loaded Docker images, and no-pull startup controls.
- [x] 3.2 Add a local-only Playwright shell lane that proves Engine/API/Web startup and core navigation without repository or registry network access.
- [x] 3.3 Add an optional separately labelled live-network random public GitHub repository lane that cannot override an offline failure.

## 4. Package, Workflow, History, And Documentation

- [x] 4.1 Include offline prepare/verify/rehearsal commands and browser assets in the runnable package manifest while preserving the same runtime manifest identity model.
- [x] 4.2 Extend readiness history, index, trend, and tests with bounded offline bundle evidence while excluding large cache payloads.
- [x] 4.3 Extend the Windows package workflow with bounded offline contract/rehearsal checks and retained reports, without committing or automatically publishing large bundles.
- [x] 4.4 Update package, release, delivery, operator, and offline installation documentation with commands, size/retention guidance, failure recovery, and proof boundaries.

## 5. Validation And Closeout

- [x] 5.1 Add deterministic tests for successful preparation/verification, command failure, package/platform mismatch, tampering, unsafe paths, missing categories, malformed SBOM, incomplete cache consumption, and evidence-history behavior.
- [x] 5.2 Run focused and full engine/API/web tests, typecheck, canonical pre-release, benchmark fixture, guardrail, and OpenSpec strict validation.
- [x] 5.3 Build a real offline bundle, consume it from an isolated package copy with registry access denied, start the stack, and complete visible Chrome local-shell plus fresh random GitHub repository core-loop evidence.
- [x] 5.4 Archive bounded evidence, update the completion taskbook, dated update log, readiness history, and next-development plan without committing cache payloads or local paths.
- [x] 5.5 Archive the OpenSpec change, commit scoped files, push the stacked branch, create a draft PR, and inspect normal CI plus package/offline rehearsal GitHub Actions on the final SHA.
