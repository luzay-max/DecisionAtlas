## ADDED Requirements

### Requirement: Readiness history archives versioned release artifact evidence
Readiness evidence history SHALL support versioned self-hosted release artifact publication and verification as an explicit durable evidence family.

#### Scenario: Release artifact evidence is supplied
- **WHEN** history archival receives publication and verification JSON/Markdown plus optional checksum and SBOM paths
- **THEN** the entry SHALL copy the bounded files, record artifact verification status, version, commit, archive names and hashes, SBOM component counts, proof level, blockers, warnings, and linked filenames

#### Scenario: Release artifact evidence is omitted
- **WHEN** history archival does not receive versioned release artifact evidence
- **THEN** the history entry SHALL mark the family `not_provided` and SHALL NOT search scratch output for a substitute

#### Scenario: Independent runner evidence is archived
- **WHEN** release artifacts were produced on a GitHub-hosted or other independent runner without customer ownership
- **THEN** the history entry SHALL preserve `is_customer_controlled=false` and SHALL NOT summarize the evidence as customer-host proof
