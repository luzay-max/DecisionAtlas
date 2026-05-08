## ADDED Requirements

### Requirement: Release baseline validation can reference generated evidence bundles
Release-facing validation records SHALL be able to reference generated release evidence bundles without replacing the canonical release gate.

#### Scenario: Bundle summarizes canonical release gate
- **WHEN** a release evidence bundle includes canonical pre-release validation status
- **THEN** release-facing documentation MAY reference the bundle as supporting evidence
- **AND** the canonical pre-release validation result SHALL remain visible as its own required gate.

#### Scenario: Bundle keeps confidence layers separate
- **WHEN** the evidence bundle includes OpenSpec validation, governance guardrail status, benchmark results, and targeted test summaries
- **THEN** the bundle SHALL preserve which results are required gates and which results are advisory confidence layers.

#### Scenario: Advisory evidence requires disclosure
- **WHEN** advisory evidence reports `caution`, `warning`, `pause`, or an equivalent non-clean status
- **THEN** release-facing documentation that references the bundle SHALL disclose that status before making a positive readiness claim.

#### Scenario: Bundle does not replace manual release decision
- **WHEN** all generated evidence is present
- **THEN** the bundle SHALL support the release decision
- **AND** the bundle SHALL NOT automatically publish, archive, tag, or approve a release.
