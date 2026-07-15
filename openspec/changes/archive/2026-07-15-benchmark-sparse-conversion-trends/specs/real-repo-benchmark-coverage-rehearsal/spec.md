## MODIFIED Requirements

### Requirement: Coverage rehearsal orchestrates benchmark artifacts
The system SHALL provide a real-repo benchmark coverage rehearsal command that produces or references current report, snapshot, comparison, sparse trend, and top-level rehearsal artifacts.

#### Scenario: Offline current report is supplied
- **WHEN** an operator supplies a current report JSON and baseline snapshot JSON
- **THEN** the rehearsal MUST generate snapshot, comparison, sparse trend, and top-level JSON/Markdown artifacts without calling GitHub, model providers, or local API endpoints

#### Scenario: Live local API mode is explicit
- **WHEN** an operator requests live mode
- **THEN** the rehearsal MUST run against the local API only after an explicit live flag and MUST record the target base URL, selected repo ids, and sparse metric source status
