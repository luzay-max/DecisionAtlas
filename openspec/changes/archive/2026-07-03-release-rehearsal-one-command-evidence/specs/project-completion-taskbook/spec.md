## ADDED Requirements

### Requirement: Completion taskbook reflects one-command release rehearsal
The completion taskbook SHALL update release evidence status when the one-command release rehearsal exists.

#### Scenario: One-command rehearsal is implemented
- **WHEN** the release rehearsal change is archived
- **THEN** the taskbook SHALL cite the script, tests, smoke output, and remaining evidence boundary.

#### Scenario: Release rehearsal remains warning
- **WHEN** the rehearsal produces warning because optional lanes are missing or non-clean
- **THEN** the taskbook SHALL keep full product completion open and list the next hardening item.
