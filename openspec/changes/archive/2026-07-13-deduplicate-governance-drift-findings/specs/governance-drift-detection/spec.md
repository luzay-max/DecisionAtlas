## MODIFIED Requirements

### Requirement: Governance drift detector returns structured advisory results
The system SHALL return a structured advisory result containing overall status, semantically deduplicated evidence-linked signals, human decision points, recommended next actions, recurrence metadata, and machine-readable output. Status and recommendation computation SHALL use the canonical signal set rather than pre-deduplication occurrences.

#### Scenario: Clean report
- **WHEN** no meaningful drift signals are found
- **THEN** the report SHALL return `status: clean` with an empty or informational signal list

#### Scenario: Watch report
- **WHEN** weak or ambiguous canonical drift signals are found
- **THEN** the report SHALL return `status: watch` with non-blocking signals that explain what should be reviewed later

#### Scenario: Drift detected report
- **WHEN** evidence shows concrete inconsistency between governance sources or repeated known issues
- **THEN** the report SHALL return `status: drift_detected` with canonical evidence-linked signals and recommended human review steps

#### Scenario: Review required report
- **WHEN** canonical drift evidence indicates that a human decision is needed before governance context can be trusted
- **THEN** the report SHALL return `status: review_required` and include `human_decisions_needed`

#### Scenario: Result is machine-readable
- **WHEN** the detector completes
- **THEN** it SHALL produce a machine-readable result containing `status`, `signals`, `human_decisions_needed`, `recommended_next_actions`, and `context`, with additive occurrence and source counts on canonical recurring signals

#### Scenario: Downstream summaries use canonical findings
- **WHEN** guardrail, dashboard, CLI, or release-evidence consumers summarize a drift report
- **THEN** each consumer SHALL derive counts and actions from the same canonical signal set
