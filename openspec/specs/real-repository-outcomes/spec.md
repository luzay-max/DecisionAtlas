## ADDED Requirements

### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users can tell whether a real repository run is ready for review, still evidence-limited, or blocked by low-yield extraction conversion rather than true lack of repository signal.

#### Scenario: Imported workspace is ready for review
- **WHEN** a live analysis run completes and the imported workspace contains reviewable candidate decisions
- **THEN** the workspace read model SHALL identify that the strongest next action is to review those candidate decisions

#### Scenario: Imported workspace is evidence-limited
- **WHEN** a live analysis run completes without enough accepted or candidate decisions to support meaningful downstream usage and the run did not show significant screened-in extraction loss
- **THEN** the workspace read model SHALL report that the workspace is evidence-limited and SHALL provide a next-step explanation rather than implying the run is fully ready

#### Scenario: Imported workspace is conversion-limited
- **WHEN** a live analysis run completes after many screened-in or full extraction attempts but still yields no reviewable candidate decisions
- **THEN** the workspace read model SHALL expose that the workspace is conversion-limited and SHALL explain that extraction quality, not only repository evidence coverage, limited the result

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, SHALL distinguish partially supported answers from truly insufficient evidence, and SHALL otherwise fail with an actionable explanation.

#### Scenario: Imported why-answer is grounded in accepted decisions
- **WHEN** the user asks a why-question in an imported workspace that has accepted decisions and matching source references
- **THEN** the system SHALL answer using those accepted decisions, SHALL identify a primary accepted decision for the answer, and SHALL return citations with the answer

#### Scenario: Imported why-answer has limited support
- **WHEN** the user asks a why-question in an imported workspace, the system selects a primary accepted decision, and only partial but still grounded citation support is available
- **THEN** the system SHALL return an explicit `limited_support` outcome instead of mislabeling the result as fully supported or as completely insufficient

#### Scenario: Imported why-search lacks accepted grounding
- **WHEN** the user asks a why-question in an imported workspace that does not yet have accepted decision grounding for the question
- **THEN** the system SHALL return an explicit evidence-limited or review-required outcome instead of a weak freeform answer

#### Scenario: Imported why-answer keeps related but distinct decisions separate
- **WHEN** the user asks a focused why-question and retrieval also finds nearby but distinct accepted decisions
- **THEN** the system SHALL keep those distinct decisions out of the main answer unless they qualify as supporting context for the same rationale thread

### Requirement: Imported drift evaluation is operationally usable
The system SHALL expose drift evaluation state for imported workspaces so users can run it intentionally and interpret the result correctly.

#### Scenario: User can evaluate drift for an imported workspace
- **WHEN** the user requests drift evaluation for an imported workspace
- **THEN** the system SHALL execute drift evaluation for that workspace and report whether alerts were created

#### Scenario: Drift page distinguishes unevaluated from no-alert result
- **WHEN** the imported workspace drift surface is shown before or after evaluation
- **THEN** the system SHALL distinguish between a workspace that has not been evaluated yet and a workspace that was evaluated but produced no current alerts
