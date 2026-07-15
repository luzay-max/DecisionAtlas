## ADDED Requirements

### Requirement: Warning lanes are classified without changing source outcomes
The system SHALL classify random repository release evidence warning lanes into actionable categories while preserving each source lane status.

#### Scenario: Mixed warning lanes are reduced
- **WHEN** the warning-lane reducer receives full-chain, multi-repo diagnosis, release rehearsal, or external-host trial JSON evidence
- **THEN** it SHALL emit JSON containing source lane IDs, source statuses, classification categories, rationale, and top-level status without downgrading warning, operator-guided, not-provided, or blocking source states.

#### Scenario: Blocking source is present
- **WHEN** any source lane has blocking status
- **THEN** the reducer SHALL report top-level `blocking` and include that lane in the blocking category.

### Requirement: Warning reduction produces operator-readable evidence
The system SHALL write Markdown evidence that summarizes warning category counts and recommended follow-up actions.

#### Scenario: Markdown report is generated
- **WHEN** the reducer is run with a Markdown output path
- **THEN** it SHALL write a customer-safe report containing overall status, selected repository identifiers when available, category counts, source evidence paths, and prioritized reduction actions.

#### Scenario: Optional source evidence is absent
- **WHEN** an optional source JSON path is not provided or does not exist
- **THEN** the reducer SHALL mark that source as `not_provided` and SHALL NOT claim that the corresponding release lane was validated.

### Requirement: Reduction actions are prioritized
The system SHALL produce a prioritized action list that separates product fixes from operator or environment follow-up.

#### Scenario: Product-controlled warnings exist
- **WHEN** warning lanes indicate import quality, review evidence, drift evaluation, guardrail, candidate support, or why-answer quality issues
- **THEN** the reducer SHALL include P0 or P1 product-controlled actions before lower-priority disclosure-only actions.

#### Scenario: Operator-guided warnings exist
- **WHEN** warning lanes indicate hosted readiness, customer-host proof, placeholder host data, or manual browser proof
- **THEN** the reducer SHALL include operator-guided actions that ask for real host observations or explicit release disclosure.
