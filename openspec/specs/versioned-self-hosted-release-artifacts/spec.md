# versioned-self-hosted-release-artifacts Specification

## Purpose
TBD - created by archiving change publish-versioned-self-hosted-artifacts. Update Purpose after archive.
## Requirements
### Requirement: Verified packages can be published as portable versioned archives
The system SHALL publish a verified runnable self-hosted package as ZIP and tar.gz archives with one stable versioned root directory and the same logical member set.

#### Scenario: Valid package is published
- **WHEN** an operator supplies a package whose offline verifier status is `pass`, a version label, and an output directory
- **THEN** the publisher SHALL create versioned ZIP and tar.gz archives, a release manifest, an SBOM, a SHA-256 checksum file, and bounded JSON/Markdown publication evidence

#### Scenario: Input package is not valid
- **WHEN** the input package verifier reports `blocking` or required package identity is missing
- **THEN** the publisher SHALL stop without reporting release-artifact pass

#### Scenario: Version label is unsafe
- **WHEN** a version label contains path separators, traversal segments, control characters, or unsupported characters
- **THEN** the publisher SHALL reject it before creating output files

### Requirement: Release artifacts carry deterministic integrity metadata
The system SHALL describe release identity and content integrity using deterministic metadata and SHA-256 hashes.

#### Scenario: Release manifest is generated
- **WHEN** archives are published
- **THEN** `release-artifacts.json` SHALL record schema version, project, version, commit, package content digest, archive root, source-date epoch, artifact filenames, sizes, SHA-256 hashes, and proof boundaries

#### Scenario: Checksums are generated
- **WHEN** release artifacts are complete
- **THEN** `SHA256SUMS` SHALL cover both archives, the SBOM, and the release manifest using stable sorted entries

#### Scenario: Identical input is published twice
- **WHEN** package bytes, version, commit, source-date epoch, and toolchain are unchanged
- **THEN** repeated publication SHALL produce identical archive, SBOM, manifest, and checksum bytes

### Requirement: Publication includes a bounded CycloneDX SBOM
The system SHALL generate a deterministic CycloneDX JSON SBOM from the package application identity and locked Node/Python dependencies without network access.

#### Scenario: Lockfiles are present
- **WHEN** `pnpm-lock.yaml` and `services/engine/uv.lock` are available in the verified package
- **THEN** the SBOM SHALL contain sorted npm and PyPI components with names, versions, package URLs when derivable, stable bom references, and lockfile SHA-256 properties

#### Scenario: SBOM scope is reviewed
- **WHEN** an operator reads publication evidence
- **THEN** the system SHALL disclose that OS packages, container images, runtime plugins, vulnerability analysis, and cryptographic signing are not provided by this SBOM lane

### Requirement: Release artifacts are verified before handoff
The system SHALL provide a fail-closed verifier for checksums, archive safety, member parity, SBOM structure, and the embedded package contract.

#### Scenario: Valid artifact bundle is verified
- **WHEN** checksums match, ZIP and tar.gz contain the same safe members under the declared root, SBOM structure is valid, and both extracted package copies pass the package verifier
- **THEN** the verifier SHALL emit `pass` JSON/Markdown evidence with zero blockers

#### Scenario: Artifact bytes are modified
- **WHEN** an archive, manifest, or SBOM hash differs from `SHA256SUMS` or the release manifest
- **THEN** the verifier SHALL report `blocking` with the affected artifact and SHALL NOT extract or trust the bundle

#### Scenario: Archive member is unsafe
- **WHEN** an archive contains an absolute path, traversal, backslash path, duplicate member, symlink, special file, unexpected root, forbidden secret/cache path, or ZIP/tar member mismatch
- **THEN** the verifier SHALL report `blocking` before writing unsafe content

### Requirement: Independent-runner publication preserves customer proof boundaries
The release-artifact workflow SHALL distinguish package distribution evidence from customer-controlled installation evidence.

#### Scenario: GitHub-hosted workflow passes
- **WHEN** a GitHub-hosted Windows runner builds, verifies, publishes, and re-verifies the release bundle
- **THEN** evidence SHALL report proof level `independent_runner_release_artifact` and `is_customer_controlled=false`

#### Scenario: Customer-host evidence is absent
- **WHEN** no external/customer-controlled installation report is attached
- **THEN** publication evidence SHALL NOT claim customer-host, air-gapped installation, private-repository, hosted URL, signing, or long-term upgrade proof
