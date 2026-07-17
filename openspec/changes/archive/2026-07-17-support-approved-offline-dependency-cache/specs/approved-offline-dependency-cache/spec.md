## ADDED Requirements

### Requirement: Online preparation creates a package-bound offline dependency bundle
The system SHALL prepare an offline dependency bundle from an already verified runnable package while network access is available and SHALL bind the bundle to the unchanged package runtime manifest and lockfiles.

#### Scenario: Complete bundle is prepared
- **WHEN** an operator prepares a bundle for a verified package with all required tools and registries available
- **THEN** the bundle SHALL record the package version, commit, package manifest SHA-256, lockfile SHA-256 values, platform contract, generated timestamp, and all required cache categories

#### Scenario: Package input is invalid
- **WHEN** package verification fails or required lockfiles/runtime metadata are absent
- **THEN** preparation SHALL stop before retaining a bundle and SHALL report blocking reasons

### Requirement: Bundle uses approved tool-native cache categories
The offline bundle SHALL contain explicit pnpm store, uv cache, Playwright browser, and allowlisted container image categories produced by bounded commands.

#### Scenario: Dependencies are materialized online
- **WHEN** bundle preparation runs successfully
- **THEN** pnpm SHALL be fetched from `pnpm-lock.yaml`, uv SHALL be populated from `uv.lock`, Playwright SHALL install the locked browser under a dedicated path, and Compose images SHALL be inspected and saved from allowlisted references

#### Scenario: Required category is missing
- **WHEN** any required category is empty, omitted, or reports a failed preparation command
- **THEN** the bundle SHALL be blocking and SHALL NOT be reported as offline-ready

### Requirement: Bundle integrity and provenance are fail closed
The system SHALL generate exact SHA-256 coverage and a CycloneDX 1.6 SBOM and SHALL reject unsafe, unexpected, unbound, or modified bundle contents.

#### Scenario: Bundle verification succeeds
- **WHEN** the manifest, checksums, SBOM, payload inventory, package bindings, platform contract, and category summaries all match
- **THEN** verification SHALL report pass with bounded counts, sizes, tool versions, proof level, and no unnecessary absolute paths

#### Scenario: Payload is tampered or unsafe
- **WHEN** a payload is modified, unlisted, missing, duplicated by case, a symlink/special file, path-traversing, secret-like, or outside its approved category
- **THEN** verification SHALL report blocking before any dependency is installed or image is loaded

#### Scenario: SBOM or package binding differs
- **WHEN** SBOM structure is malformed or package manifest/lockfile hashes differ from the selected package
- **THEN** verification SHALL report blocking and identify the mismatched contract field

### Requirement: Offline consumption installs without registry access
The system SHALL consume a verified bundle from an isolated package copy using package-manager offline modes, a dedicated browser path, locally loaded container images, and process-level registry network denial.

#### Scenario: Offline installation and startup pass
- **WHEN** a platform-compatible complete bundle is consumed with registry proxy variables directed to a blackhole endpoint and localhost exempted
- **THEN** pnpm and uv installation SHALL use offline flags, Docker SHALL use loaded images without pulling, Engine/API/Web SHALL reach health gates, and a local-only browser shell SHALL pass

#### Scenario: Cache is incomplete
- **WHEN** a required package, Python distribution, browser executable, or container image is unavailable during offline consumption
- **THEN** the rehearsal SHALL fail closed with the failing stage and bounded command diagnostics

#### Scenario: Platform or toolchain differs
- **WHEN** the consumer OS, architecture, Python major/minor, Node major, pnpm, uv, or Playwright version violates the bundle platform contract
- **THEN** consumption SHALL stop before installation and SHALL report the exact incompatibility

### Requirement: Offline and live-network evidence remain distinguishable
Offline dependency evidence SHALL distinguish local process-enforced installation/startup proof from later live repository and customer-host proof.

#### Scenario: Live public repository regression follows offline proof
- **WHEN** an operator re-enables network after a passing offline lane and runs the imported-workspace core loop against a fresh random public GitHub repository
- **THEN** the report SHALL preserve separate offline and live-network lane statuses and SHALL NOT use live success to override an offline failure

#### Scenario: Customer host is absent
- **WHEN** the rehearsal runs on a maintainer workstation or GitHub-hosted runner
- **THEN** evidence SHALL set `is_customer_controlled=false` and SHALL NOT claim physical air-gap, customer installation, private repository, signing, or vulnerability proof

### Requirement: Large cache payloads remain outside source history
The system SHALL retain offline dependency payloads as operator or CI artifacts and SHALL archive only bounded evidence into Git-tracked readiness history.

#### Scenario: Evidence is archived
- **WHEN** offline bundle preparation, verification, and rehearsal evidence is archived
- **THEN** history SHALL copy bounded JSON/Markdown, checksum summary, and SBOM files but SHALL NOT copy pnpm stores, uv caches, browser binaries, container image tar files, secrets, databases, or raw repository content
