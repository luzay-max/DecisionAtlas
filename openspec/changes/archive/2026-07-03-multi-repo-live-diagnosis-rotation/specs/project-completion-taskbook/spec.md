## ADDED Requirements

### Requirement: Completion taskbook reflects multi-repo diagnosis rotation
The completion taskbook SHALL update real GitHub repository validation status when multi-repo diagnosis rotation exists.

#### Scenario: Multi-repo diagnosis is implemented
- **WHEN** multi-repo diagnosis rotation is archived
- **THEN** the taskbook SHALL cite the script, tests, smoke evidence, and remaining evidence boundary.

#### Scenario: Multi-repo diagnosis remains warning
- **WHEN** selected repositories produce warning or operator-guided results
- **THEN** the taskbook SHALL keep full product completion open and list the next quality or release-evidence step.
