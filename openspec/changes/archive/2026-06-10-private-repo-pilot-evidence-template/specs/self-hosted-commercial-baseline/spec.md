## ADDED Requirements

### Requirement: Self-hosted commercial baseline distinguishes private-repo proof from template readiness
The self-hosted commercial baseline SHALL distinguish having a private-repo pilot evidence workflow from having completed a real private-repo pilot in a customer-controlled environment.

#### Scenario: Commercial baseline describes private-repo evidence
- **WHEN** self-hosted commercial documentation references private-repo pilot evidence
- **THEN** it SHALL state that the committed template and verifier prove evidence readiness only
- **AND** it SHALL require actual private-repo proof to be generated locally or in the customer-controlled environment without committing private content or credentials.

#### Scenario: Private-repo evidence is absent
- **WHEN** a customer-facing self-hosted claim lacks sanitized private-repo pilot evidence
- **THEN** the baseline SHALL require the claim to disclose the missing evidence and avoid describing private-repo readiness as clean pass.
