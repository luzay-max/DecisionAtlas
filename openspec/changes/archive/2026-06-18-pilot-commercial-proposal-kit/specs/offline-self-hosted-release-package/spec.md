## ADDED Requirements

### Requirement: Self-hosted package includes proposal kit templates
The offline self-hosted release package SHALL include or reference pilot commercial proposal kit template materials for paid pilot handoff.

#### Scenario: Package is prepared for paid pilot handoff
- **WHEN** a self-hosted package is built for a paid pilot or commercial evaluation
- **THEN** the package SHALL include proposal kit entry point, quote assumptions, acceptance checklist, support boundary, renewal or upgrade path, and verifier command references.

#### Scenario: Package excludes customer-specific terms
- **WHEN** proposal kit materials are included in the package
- **THEN** the package SHALL exclude filled customer-specific pricing, payment data, signed legal terms, private repository secrets, and private source content.
