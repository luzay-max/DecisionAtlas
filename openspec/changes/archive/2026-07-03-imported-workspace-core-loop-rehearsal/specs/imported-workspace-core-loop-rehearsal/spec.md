## ADDED Requirements

### Requirement: Imported workspace core loop evidence is generated
The system SHALL generate evidence for an imported workspace moving through the core DecisionAtlas loop.

#### Scenario: Core loop is probed
- **WHEN** an operator supplies a repository, workspace slug, or public import rehearsal artifact
- **THEN** the system SHALL probe setup/reuse, dashboard, review, why-search, drift, and guardrail lanes and write JSON plus Markdown evidence.

#### Scenario: Workspace cannot be resolved
- **WHEN** the workspace slug cannot be derived from input, lookup, or import rehearsal evidence
- **THEN** the system SHALL emit non-pass evidence with the required next action rather than failing silently.

### Requirement: Imported workspace core loop preserves lane boundaries
The core-loop evidence SHALL preserve the status and limitation of each lane.

#### Scenario: Some lanes are not clean
- **WHEN** review, why-search, drift, guardrail, provider, or local stack checks are unavailable or inconclusive
- **THEN** the report SHALL classify those lanes as `warning`, `operator_guided`, `not_provided`, `provider_failure`, or `local_stack_failure` instead of `pass`.

#### Scenario: Core loop is clean enough for release evidence
- **WHEN** setup/reuse, dashboard, review, why-search, and drift lanes all produce usable evidence and guardrail is continue or caution
- **THEN** the report SHALL expose enough summary data for readiness history or release rehearsal to include it.

### Requirement: Imported workspace core loop is safe for customer review
The core-loop evidence SHALL avoid leaking secrets or raw private repository contents.

#### Scenario: Markdown report is written
- **WHEN** the Markdown report is generated
- **THEN** it SHALL include compact lane statuses, counts, and next actions without embedding tokens, raw model output, or private source text.
