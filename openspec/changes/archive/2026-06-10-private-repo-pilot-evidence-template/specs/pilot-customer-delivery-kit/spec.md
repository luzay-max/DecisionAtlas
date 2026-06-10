## ADDED Requirements

### Requirement: Pilot kit references private-repo pilot evidence template
The pilot customer delivery kit SHALL reference the private-repository pilot evidence template when private-repo validation is part of the pilot claim.

#### Scenario: Private-repo pilot is claimed
- **WHEN** the pilot kit, delivery email, handoff material, or sales material claims that a private repository has been evaluated
- **THEN** it SHALL point to sanitized private-repo pilot evidence or explicitly state that private-repo proof is still operator-guided or not provided.

#### Scenario: Pilot kit verification runs with private-repo evidence
- **WHEN** the pilot kit verifier runs
- **THEN** it SHALL require the private-repo pilot evidence template to exist
- **AND** it SHALL preserve customer-specific private-repo evidence as `operator_guided` or `not_provided` unless a sanitized evidence file is explicitly supplied.
