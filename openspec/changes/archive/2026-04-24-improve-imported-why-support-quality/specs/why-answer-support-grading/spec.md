## MODIFIED Requirements

### Requirement: Support grading preserves full-support semantics
The system SHALL preserve a stronger fully supported why-answer state so users can distinguish between answers that are directionally correct and answers that are strongly grounded, SHALL evaluate imported why support as a bounded support bundle centered on one primary accepted decision, SHALL allow retrieval-backed supporting evidence from the same rationale thread to improve support quality without weakening the meaning of `ok` or `limited_support`, and SHALL allow an imported workspace with a newly established accepted baseline to satisfy those support states only when the asked rationale thread is grounded to that accepted decision.

#### Scenario: Fully supported answer remains distinct from partial support
- **WHEN** an imported why-answer satisfies the threshold for a fully supported grounded answer
- **THEN** the system SHALL return `ok` rather than `limited_support`

#### Scenario: Better source-ref coverage upgrades support state
- **WHEN** a why-answer previously had only partial support because the matched decision retained too few grounded refs and a later extraction run improves that grounded coverage
- **THEN** the system SHALL allow the answer to move from `limited_support` to `ok` without weakening the meaning of either state

#### Scenario: Retrieval-backed evidence can strengthen support
- **WHEN** a why-answer already has a correct primary accepted decision and later retrieval improvements find stronger supporting evidence for that same rationale thread
- **THEN** the system SHALL allow that answer to satisfy the stronger support state without changing the trust anchor away from the accepted decision

#### Scenario: First accepted baseline does not auto-upgrade support
- **WHEN** an imported workspace establishes its first accepted decision but the asked why-question is not sufficiently grounded to that accepted rationale thread
- **THEN** the system SHALL not upgrade the answer to `ok` or `limited_support` solely because the workspace now contains an accepted baseline

#### Scenario: First accepted baseline can unlock a bounded supported answer
- **WHEN** an imported workspace establishes its first accepted decision and a why-question can be grounded to that accepted decision with sufficient citation support
- **THEN** the system SHALL allow the imported why-answer to return `limited_support` or `ok` according to the existing support thresholds

#### Scenario: One grounded ref plus same-thread chunk support can satisfy full support
- **WHEN** the primary accepted decision has one grounded source ref and additional chunk-backed evidence that supports the same rationale thread strongly enough
- **THEN** the system SHALL be able to return `ok` without requiring a second direct source ref

#### Scenario: Weak post-acceptance match stays evidence-limited
- **WHEN** an imported workspace has an accepted baseline but the selected answer cannot assemble enough same-thread support for the asked rationale
- **THEN** the system SHALL return `evidence_limited` rather than upgrading the response to `limited_support`
