## Purpose
Provide a local, advisory governance drift report that helps developers and future AI agents detect long-term inconsistencies between roadmap direction, main OpenSpec specs, archived changes, accepted governance rules, update logs, postmortems, and optional current diff context.

## Requirements

### Requirement: Governance drift detector analyzes long-term governance context
The system SHALL provide a local governance drift report that analyzes bounded project governance context across roadmap documents, main OpenSpec specs, archived OpenSpec changes, accepted governance rules, update logs, postmortem-style documents, and optional current workspace diff context.

#### Scenario: Report collects roadmap and spec context
- **WHEN** a developer runs the governance drift detector in a repository with roadmap documents and main OpenSpec specs
- **THEN** the report SHALL include bounded references to those roadmap and spec sources as governance context

#### Scenario: Report collects archived change context
- **WHEN** archived OpenSpec changes exist in the repository
- **THEN** the report SHALL inspect bounded proposal, design, task, and spec delta content from those archived changes for governance history signals

#### Scenario: Report can include current diff context
- **WHEN** the repository has staged, unstaged, or untracked workspace changes
- **THEN** the detector MAY include current diff paths and excerpts as recent evidence without treating the report as a merge gate

### Requirement: Governance drift detector identifies explainable drift signals
The system SHALL identify explainable governance drift signals and SHALL attach source references to each signal.

#### Scenario: Roadmap mismatch signal
- **WHEN** recent changes or archived change history emphasize work that appears outside the current roadmap direction
- **THEN** the report SHALL produce a `roadmap_mismatch` signal with roadmap and change evidence references

#### Scenario: Spec gap signal
- **WHEN** archived changes or recent work indicate new behavior that is not reflected in main OpenSpec specs
- **THEN** the report SHALL produce a `spec_gap` signal that names the likely missing or stale spec context

#### Scenario: Stale rule signal
- **WHEN** deprecated, superseded, or rejected governance sources appear to be reused as active guidance
- **THEN** the report SHALL produce a `stale_rule` signal instead of treating that source as authoritative enforcement input

#### Scenario: Repeated postmortem issue signal
- **WHEN** update logs, postmortems, or error summaries describe a prior issue and similar evidence appears again in recent context
- **THEN** the report SHALL produce a `repeated_postmortem_issue` signal with references to both prior and recent evidence

#### Scenario: Unsynced human decision signal
- **WHEN** proposal, design, task, update-log, or roadmap text appears to contain a human decision that is not reflected in main specs or accepted governance rules
- **THEN** the report SHALL produce an `unsynced_decision` signal that recommends human review rather than automatically creating a rule

### Requirement: Governance drift detector returns structured advisory results
The system SHALL return a structured advisory result containing overall status, evidence-linked signals, human decision points, recommended next actions, and machine-readable output.

#### Scenario: Clean report
- **WHEN** no meaningful drift signals are found
- **THEN** the report SHALL return `status: clean` with an empty or informational signal list

#### Scenario: Watch report
- **WHEN** weak or ambiguous drift signals are found
- **THEN** the report SHALL return `status: watch` with non-blocking signals that explain what should be reviewed later

#### Scenario: Drift detected report
- **WHEN** evidence shows concrete inconsistency between governance sources or repeated known issues
- **THEN** the report SHALL return `status: drift_detected` with evidence-linked signals and recommended human review steps

#### Scenario: Review required report
- **WHEN** drift evidence indicates that a human decision is needed before governance context can be trusted
- **THEN** the report SHALL return `status: review_required` and include `human_decisions_needed`

#### Scenario: Result is machine-readable
- **WHEN** the detector completes
- **THEN** it SHALL produce a machine-readable result containing `status`, `signals`, `human_decisions_needed`, `recommended_next_actions`, and `context`

### Requirement: Governance drift detector remains advisory by default
The system SHALL keep governance drift detection advisory by default and SHALL NOT automatically modify code, update specs, rewrite rules, create rules, or block CI unless a future explicit change enables that behavior.

#### Scenario: Detector does not modify governance artifacts
- **WHEN** the detector finds drift signals
- **THEN** it SHALL NOT modify OpenSpec files, roadmap documents, governance documents, or accepted rules automatically

#### Scenario: Detector does not promote inferred decisions
- **WHEN** the detector finds an unsynced human decision
- **THEN** it SHALL recommend review and synchronization rather than automatically promoting that decision to an accepted rule

#### Scenario: Detector is not a default CI gate
- **WHEN** project validation runs through the existing default release or test commands
- **THEN** governance drift findings SHALL NOT block those commands unless a future change explicitly wires the detector into CI

### Requirement: Governance drift detector surfaces lifecycle misuse
The system SHALL surface stale or superseded governance rule reuse as advisory drift evidence that asks for human review instead of mutating rule lifecycle automatically.

#### Scenario: Superseded rule reuse produces lifecycle signal
- **WHEN** recent change context, archived change text, roadmap text, or governance documentation appears to reuse a superseded governance rule as active guidance
- **THEN** the drift detector SHALL produce a source-linked `stale_rule` or equivalent lifecycle signal that identifies the superseded rule, its replacement when known, and the human decision needed

#### Scenario: Stale rule reuse produces lifecycle signal
- **WHEN** recent context appears to reuse a stale governance rule as active guidance
- **THEN** the drift detector SHALL produce a source-linked lifecycle signal that asks whether the rule should remain stale, be restored through a new explicit decision, or be replaced by a new accepted rule

#### Scenario: Lifecycle drift remains advisory
- **WHEN** lifecycle misuse is detected
- **THEN** the drift detector SHALL NOT automatically update lifecycle status, create replacement rules, rewrite specs, or block CI by default

#### Scenario: Guardrail can ask a concrete lifecycle question
- **WHEN** lifecycle misuse causes the agent guardrail to include drift evidence
- **THEN** the resulting human question or recommended action SHALL clearly ask what to do with the stale or superseded rule rather than treating the inactive rule as authoritative enforcement input
