## ADDED Requirements

### Requirement: Package includes license and support boundary artifacts
The self-hosted package SHALL include license/support boundary documentation and entitlement template references.

#### Scenario: Package includes boundary docs
- **WHEN** a self-hosted package is built
- **THEN** it SHALL include customer-readable license/support boundary documentation and an offline entitlement template

#### Scenario: Package verifier records boundary lane
- **WHEN** a package verifier evaluates a self-hosted package
- **THEN** it SHALL record whether license/support boundary evidence is present and SHALL keep entitlement absence non-blocking for evaluation
