# Offline Dependency Bundle Guide

DecisionAtlas keeps the runnable source release separate from its platform-specific dependency cache. Prepare the cache on a trusted machine with network access, transfer both artifacts, verify their package binding and checksums, then consume the cache with offline package-manager modes.

## Prepare Online

From the runnable package root:

```powershell
python scripts\ci\prepare_offline_dependency_bundle.py `
  --package . `
  --output-dir C:\DecisionAtlas\offline-bundle `
  --output-json .tmp\offline-dependency-preparation.json `
  --output-markdown .tmp\offline-dependency-preparation.md
```

Preparation creates dedicated pnpm, uv, Playwright Chromium, and Docker image payloads plus `offline-dependency-bundle.json`, `SHA256SUMS`, and a CycloneDX 1.6 SBOM. It does not reuse arbitrary global developer cache directories.

## Verify Before Transfer Or Use

```powershell
python scripts\ci\verify_offline_dependency_bundle.py `
  --package . `
  --bundle C:\DecisionAtlas\offline-bundle `
  --output-json .tmp\offline-dependency-verification.json `
  --output-markdown .tmp\offline-dependency-verification.md
```

Verification is fail closed for package/lockfile mismatch, platform or tool version mismatch, missing categories, unlisted or modified files, unsafe paths, symlinks, malformed SBOM, and checksum differences. Never copy only part of a bundle or merge it with a developer cache.

## Rehearse Offline Consumption

```powershell
python scripts\ci\rehearse_offline_self_hosted_install.py `
  --package . `
  --bundle C:\DecisionAtlas\offline-bundle `
  --label offline-install `
  --output-json .tmp\offline-self-hosted-install-rehearsal.json `
  --output-markdown .tmp\offline-self-hosted-install-rehearsal.md
```

The rehearsal copies both inputs into an isolated temporary directory, verifies them again, loads container images, runs pnpm and uv with offline flags and a blackhole registry proxy, uses the bundled Playwright browser, and starts Engine/API/Web for a local-only browser flow.

After the offline lane passes, add `--run-live-repo --repo <owner/name>` only if network has intentionally been restored. That live GitHub lane is separately labelled and cannot turn an offline failure into pass.

## Retention And Size

- Keep bundle payloads in an operator-controlled artifact store or encrypted removable media, not Git.
- Preserve the source release, bundle manifest, `SHA256SUMS`, and SBOM together.
- A bundle is valid only for its recorded OS, architecture, Python major/minor, Node major, pnpm, uv, Playwright, package commit, and lockfile hashes.
- Rebuild the bundle after any package, lockfile, toolchain, browser, or container image change.

## Boundaries

Process-level offline controls and package-manager offline flags do not prove a physical air gap. The bundle does not include the operating system, Node, Python, pnpm, uv, Docker, cryptographic signing, vulnerability analysis, private-repository credentials, customer-host installation, or cross-platform portability.
