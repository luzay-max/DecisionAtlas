## MODIFIED Requirements

### Requirement: Support grading preserves full-support semantics
The system SHALL preserve a stronger fully supported why-answer state so users can distinguish between answers that are directionally correct and answers that are strongly grounded, and SHALL improve upstream grounding density so more valid imported answers can satisfy that stronger state.

#### Scenario: Fully supported answer remains distinct from partial support
- **WHEN** an imported why-answer satisfies the threshold for a fully supported grounded answer
- **THEN** the system SHALL return `ok` rather than `limited_support`

#### Scenario: Better source-ref coverage upgrades support state
- **WHEN** a why-answer previously had only partial support because the matched decision retained too few grounded refs and a later extraction run improves that grounded coverage
- **THEN** the system SHALL allow the answer to move from `limited_support` to `ok` without weakening the meaning of either state
