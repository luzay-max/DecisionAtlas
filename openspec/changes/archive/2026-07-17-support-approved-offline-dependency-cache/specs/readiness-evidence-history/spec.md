## ADDED Requirements

### Requirement: Readiness history archives offline dependency bundle evidence
Readiness evidence history SHALL support offline dependency bundle preparation, verification, and consumption rehearsal as an explicit durable evidence family.

#### Scenario: Offline dependency evidence is supplied
- **WHEN** history archival receives bounded offline bundle JSON/Markdown, checksum summary, and CycloneDX SBOM paths
- **THEN** the entry SHALL preserve status, package version and commit, platform contract, cache category counts and sizes, proof level, offline controls, blocker and warning counts, and linked filenames

#### Scenario: Offline dependency evidence is omitted
- **WHEN** readiness archival does not receive offline dependency evidence
- **THEN** index and trend summaries SHALL mark the family `not_provided` and SHALL NOT search scratch directories or copy cache payloads as a substitute

#### Scenario: Independent runner evidence is archived
- **WHEN** an offline rehearsal runs on a maintainer or GitHub-hosted machine
- **THEN** history SHALL preserve `is_customer_controlled=false` and SHALL not summarize process-enforced offline installation as physical air-gap or customer-host proof
