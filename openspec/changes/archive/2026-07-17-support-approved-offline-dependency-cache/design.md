## Context

The runnable self-hosted package and versioned release artifacts contain exact lockfiles and runtime scripts but deliberately exclude dependency caches. Operators in restricted networks currently have no supported way to pre-stage npm packages, Python distributions, the Playwright browser, and PostgreSQL/Redis images, and copying a developer cache would be unaudited, platform-ambiguous, and difficult to verify.

The offline bundle must remain separate from the source release artifact, bind to one package manifest and platform, support fail-closed verification before consumption, and produce evidence that distinguishes process-enforced offline installation from customer-controlled or physically air-gapped proof.

## Goals / Non-Goals

**Goals:**

- Prepare all required dependency classes while network access is available.
- Bind the bundle to the package manifest, lockfiles, platform, toolchain, browser revision, and container image references.
- Verify every retained file, category, and SBOM entry before offline use.
- Install dependencies and start the application with registry access disabled by package-manager offline modes and a blackhole proxy.
- Prove a local-only browser shell lane during the offline phase, then optionally run a separately labelled live public-repository lane after network controls are removed.
- Archive bounded evidence without committing large caches or container image payloads.

**Non-Goals:**

- Cross-platform reuse of one cache bundle.
- Shipping Node, Python, pnpm, uv, Docker, or the operating system itself.
- Claiming a physically air-gapped network, customer-controlled host, private-repository access, cryptographic signing, or vulnerability analysis.
- Automatically publishing multi-gigabyte offline bundles as public GitHub Releases.

## Decisions

### Keep the offline bundle separate and bind it to the package

The bundle is a sibling artifact with its own manifest, `SHA256SUMS`, and CycloneDX SBOM. Its manifest records SHA-256 values for the source package manifest, `pnpm-lock.yaml`, `services/engine/uv.lock`, `apps/web/package.json`, and `docker-compose.yml`. Offline consumption verifies those values against the selected package before installing anything.

This preserves one runtime manifest for online and offline installation and avoids rebuilding the application release merely because cache payloads change. Embedding caches in the release ZIP was rejected because it multiplies large payloads, obscures provenance, and weakens the existing secret/cache exclusion contract.

### Use tool-native cache formats with an explicit platform contract

- pnpm is prepared with `pnpm fetch --frozen-lockfile --store-dir <bundle>/pnpm/store` and consumed with `pnpm install --offline --frozen-lockfile --store-dir ...`.
- uv is prepared by syncing into a disposable environment with a dedicated cache directory and consumed using `uv sync --offline --frozen --cache-dir ... --no-python-downloads`.
- Playwright Chromium is installed under a dedicated `PLAYWRIGHT_BROWSERS_PATH` and consumed from that exact path without invoking online browser installation.
- Compose image references are parsed from `docker-compose.yml`, restricted to an explicit allowlist, pulled online, inspected for immutable digests, and saved into one Docker image tar for later `docker image load`.

The manifest records OS, architecture, Python major/minor, Node major, pnpm version, uv version, Playwright version, and container image references. A mismatch blocks consumption. Normalizing raw cache internals was rejected because tool-native stores are content-addressed and their metadata is implementation-specific.

### Inventory every retained regular file

Preparation rejects symlinks and forbidden secret/build/database/log paths, inventories sorted relative paths, and writes exact SHA-256 and size metadata. `SHA256SUMS` covers the manifest, SBOM, and every payload file; verification requires exact coverage and rejects unlisted files, duplicates, traversal, backslashes, and case-fold collisions.

The CycloneDX 1.6 SBOM reuses lockfile-derived npm/PyPI component semantics from release artifacts and adds container image components with immutable identifiers. Checksums prove integrity relative to a trusted manifest source but do not authenticate the publisher.

### Separate offline and live-network browser lanes

The offline rehearsal copies package and bundle into an owned temporary root, verifies both, loads container images, installs Node/Python dependencies with offline flags, and runs a local-only Playwright shell test while registry proxy variables point to a blackhole endpoint and localhost remains exempt. It records the controls used and fails if any required installation/startup/browser stage fails.

After the offline lane passes, an optional live-network lane may clear the blackhole proxy and run the existing imported-workspace core loop with a fresh random public GitHub repository. Reports label the two phases separately; live repository success cannot repair an offline failure.

### Keep CI bounded

Unit and integration tests use fixture caches and injected command runners. The Windows package rehearsal validates offline bundle preparation/verification contracts with bounded fixtures and retains reports; full real cache payloads are generated locally or through explicit workflow dispatch because browser and Docker payloads can be large.

Readiness history copies only bounded manifests, checksum summaries, SBOMs, and rehearsal reports. It never copies pnpm stores, uv caches, browser binaries, image tar files, tokens, databases, or raw imported source.

## Risks / Trade-offs

- [Tool-native caches can change between pnpm/uv/Playwright versions] -> Bind bundle consumption to exact tool versions and fail with a targeted mismatch.
- [Windows proxy variables are not a kernel network namespace] -> Use package-manager offline flags, blackhole proxies, no browser egress during the offline lane, and report proof level `process_enforced_offline_install`, not physical air-gap.
- [Docker image tar and browser payloads are large] -> Keep payloads outside Git and readiness history, report category sizes, and require explicit operator retention.
- [Container tags can move] -> Record inspected image IDs/digests and verify loaded identities where the runtime exposes them.
- [Cache may be incomplete despite a valid directory] -> Perform an actual clean offline install and browser startup; missing artifacts become blocking with command-tail diagnostics.
- [A live repository test needs network] -> Run it only after the offline lane and label it as separate evidence.

## Migration Plan

1. Add shared dependency inventory helpers and offline prepare/verify/rehearsal commands.
2. Add the commands to the runnable package allowlist and manifest without changing the base release package identity model.
3. Add fixture tests, a real local generated-bundle rehearsal, and bounded workflow checks.
4. Archive the new readiness evidence family and update operator documentation.
5. Roll back by removing the supplementary offline bundle workflow; the existing online runnable package remains valid.

## Open Questions

- Whether a later commercial release should publish separate Windows and Linux offline bundles through an approval-protected release environment.
- Whether container vulnerability attestations should be added before offline bundles are offered to paid pilots.
- Whether future browser coverage should include Chrome for Testing in addition to Playwright Chromium.
