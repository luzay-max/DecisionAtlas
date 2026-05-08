## ADDED Requirements

### Requirement: Curated real-repository outcomes are comparable over time
The system SHALL allow curated real-repository validation outcomes to be compared across dated benchmark runs so maintainers can identify product-value regressions separately from operational blockers.

#### Scenario: Product value regression is identified
- **WHEN** a curated repository moves from a stronger value outcome to a weaker product-limited outcome and the current row is not operationally blocked
- **THEN** validation comparison SHALL classify the repository as regressed and include bounded evidence explaining the changed outcome or metric decline

#### Scenario: Product value improvement is identified
- **WHEN** a curated repository moves from an evidence-limited, conversion-limited, or reviewable-limited outcome to a stronger value outcome
- **THEN** validation comparison SHALL classify the repository as improved and include bounded evidence such as better readiness, stronger candidate quality, why support, or drift-case behavior

#### Scenario: Operational blocker is not counted as product regression
- **WHEN** the current benchmark row is missing-workspace or operationally blocked because of API availability, provider configuration, auth/session state, GitHub/network failure, or absent imported workspace state
- **THEN** validation comparison SHALL classify the row as operationally blocked rather than as a product-value regression

#### Scenario: Comparison avoids exact prose dependence
- **WHEN** a repository outcome is compared over time
- **THEN** the comparison SHALL use bounded statuses, counts, quality labels, citation counts, primary-thread match evidence, drift-case states, and category fields rather than exact generated answer wording
