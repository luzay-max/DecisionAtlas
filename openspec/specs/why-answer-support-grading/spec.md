## ADDED Requirements

### Requirement: Why-search grades partially supported answers separately
The system SHALL classify why-answers with a correct primary accepted decision but incomplete citation support as a distinct partially supported outcome instead of collapsing them into the same state as missing or ungrounded answers.

#### Scenario: Primary decision is correct but support is partial
- **WHEN** why-search selects a primary accepted decision and returns at least one grounded citation, but the answer does not meet the threshold for a fully supported imported why-answer
- **THEN** the system SHALL return a `limited_support` outcome for that why-answer

#### Scenario: Truly weak or missing grounding still fails closed
- **WHEN** why-search does not have enough accepted-decision grounding to support a useful imported answer
- **THEN** the system SHALL continue to return `insufficient_evidence` or `review_required` instead of upgrading the result to partial support

### Requirement: Support grading preserves full-support semantics
The system SHALL preserve a stronger fully supported why-answer state so users can distinguish between answers that are directionally correct and answers that are strongly grounded, and SHALL improve upstream grounding density so more valid imported answers can satisfy that stronger state.

#### Scenario: Fully supported answer remains distinct from partial support
- **WHEN** an imported why-answer satisfies the threshold for a fully supported grounded answer
- **THEN** the system SHALL return `ok` rather than `limited_support`

#### Scenario: Better source-ref coverage upgrades support state
- **WHEN** a why-answer previously had only partial support because the matched decision retained too few grounded refs and a later extraction run improves that grounded coverage
- **THEN** the system SHALL allow the answer to move from `limited_support` to `ok` without weakening the meaning of either state

### Requirement: Support grading is exposed through the why response contract
The system SHALL expose the support grade in the why-search result payload so downstream UI and tests can render the distinction directly.

#### Scenario: API consumers can see limited support
- **WHEN** a why-answer is partially supported
- **THEN** the why-search response SHALL carry the `limited_support` status in the same response contract used for other why outcomes
