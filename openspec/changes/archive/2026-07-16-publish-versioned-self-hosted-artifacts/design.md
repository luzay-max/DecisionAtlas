## Context

The existing package builder produces a verified runnable directory and the isolated rehearsal proves that directory can install and start outside the maintainer checkout. Delivery still depends on copying a mutable folder, so an operator cannot verify that a downloaded handoff is byte-for-byte the release that CI produced. The solution must remain Python-standard-library based, deterministic, Windows/Linux friendly, secret-safe, and honest about the difference between an independent CI runner and a customer-controlled host.

## Goals / Non-Goals

**Goals:**

- Publish one versioned ZIP and one tar.gz with the same stable root and member set.
- Generate a release manifest, SHA-256 checksum file, and CycloneDX JSON SBOM from package lockfiles.
- Verify hashes, archive safety, member parity, SBOM structure, and the extracted package contract before reporting pass.
- Produce bounded JSON/Markdown evidence locally and in GitHub Actions, then archive it in readiness history.
- Make identical input package bytes and source-date epoch produce identical output bytes.

**Non-Goals:**

- Cryptographic signing or long-lived signing-key custody.
- Bundling pnpm, uv, browser, container, or operating-system dependency caches.
- Automatic public GitHub Release creation from pull requests.
- Replacing the existing package builder/verifier or customer-host trial evidence.
- Billing, hosted multi-tenancy, Marketplace, OAuth, SSO, or runtime licensing.

## Decisions

### Separate directory packaging from artifact publication

`build_self_hosted_package.py` remains the authority for package contents. A new publisher accepts that directory, invokes `verify_package`, and refuses to archive a non-pass package. This preserves one allowlist and avoids duplicating runtime-selection logic.

Alternative considered: make the package builder also create archives. Rejected because it would couple content selection, distribution encoding, SBOM generation, and verification into one command that is harder to test and reuse.

### Publish ZIP and tar.gz with normalized metadata

The publisher sorts POSIX member paths, rejects symlinks, uses a version-derived root directory, normalizes file/directory modes, owner fields, timestamps, and gzip headers, and accepts `--source-date-epoch` or `SOURCE_DATE_EPOCH`. ZIP covers Windows operators; tar.gz covers Linux/server operators.

Alternative considered: ZIP only. Rejected because Linux operators would lose normal tar tooling and permission semantics. Platform-specific archives are also rejected because they would create different logical releases.

### Use SHA-256 plus a release manifest

The publisher records archive names, sizes, SHA-256 hashes, package content digest, root name, version, commit, and proof boundary in `release-artifacts.json`. `SHA256SUMS` covers both archives, the SBOM, and the release manifest. The checksum file does not hash itself.

Cryptographic signatures are deferred until a signing identity and key-rotation policy exist. Checksums detect corruption and tampering relative to a trusted manifest source but do not authenticate the publisher.

### Generate a bounded CycloneDX SBOM without network calls

The publisher parses `services/engine/uv.lock` with `tomllib` and reads pnpm package keys from the lockfile `packages` section. It emits sorted npm/PyPI components, purls, lockfile hashes, and the DecisionAtlas application component using CycloneDX JSON schema 1.6. No package registry or third-party SBOM binary is required.

The SBOM describes declared locked dependencies, not operating-system packages, container base images, runtime-loaded plugins, or vulnerability status. Those limitations are explicit in the release manifest and Markdown evidence.

### Verify before extraction and verify both archive formats

The verifier checks manifest/checksum consistency, duplicate or unsafe members, absolute paths, `..`, backslashes, symlink/special-file entries, stable root, ZIP/tar member parity, and secret/cache exclusion patterns. It extracts each archive into a temporary directory outside the source checkout and runs the existing package verifier on both extracted package roots.

Any mismatch is `blocking`; the verifier never keeps a package or SBOM pass when integrity or extraction safety fails.

### Preserve proof levels

GitHub Actions can produce `independent_runner_release_artifact` evidence and upload the distributable bundle. It remains `is_customer_controlled=false`. Customer installation, private credentials, offline caches, and hosted URLs require separate evidence.

## Risks / Trade-offs

- **[Lockfile parser misses an uncommon pnpm key]** → Cover scoped, peer-suffixed, and legacy keys with fixtures; retain lockfile hashes even when a component cannot be parsed.
- **[Archive output differs across Python/zlib versions]** → Normalize metadata and test repeated builds on the same runner; record Python/platform in evidence without claiming cross-toolchain byte identity.
- **[Checksum file is mistaken for authentication]** → State that SHA-256 proves integrity relative to a trusted source, not publisher identity; defer signing.
- **[Unsafe archive extraction]** → Inspect all entries before writing, reject special files/symlinks, then extract only validated normalized members.
- **[SBOM is treated as vulnerability scanning]** → Mark vulnerability analysis and OS/container inventory as `not_provided`.
- **[Large evidence artifacts inflate Git history]** → Commit only bounded manifests/reports; keep ZIP/tar.gz as CI artifacts or local `.tmp` outputs.

## Migration Plan

1. Add publisher, verifier, tests, and package documentation without changing current runtime startup.
2. Extend the package rehearsal workflow to produce and verify artifacts, then upload archives and bounded evidence.
3. Run a local repeated-build determinism test and a real extracted-package rehearsal against a fresh public repository.
4. Archive only JSON/Markdown/checksum/SBOM summaries in readiness history; do not commit large archives.
5. Roll back by removing the publication steps; the underlying runnable package directory remains usable.

## Open Questions

- Which signing mechanism should be adopted after a stable release identity exists: Sigstore keyless, minisign, or an offline GPG key?
- Should a future tagged workflow create a GitHub Release automatically, or require an explicit operator approval environment?
- Which approved cache format should be used for later air-gapped pnpm, uv, browser, and container dependencies?
