## ADDED Requirements

### Requirement: Multi-repo diagnosis reports action category counts
Multi-repo live diagnosis SHALL report action category counts for selected real repositories.

#### Scenario: Repository has setup-driven warning
- **WHEN** a selected repository has non-clean core-loop lanes while setup still requires waiting for import or operator proof
- **THEN** the repository and aggregate diagnosis SHALL include operator/setup action counts so downstream reducers do not treat the entire warning as product-controlled.

#### Scenario: Repository has product quality warning
- **WHEN** a selected repository has review, why-search, drift, or guardrail gaps not explained by setup waiting
- **THEN** the repository and aggregate diagnosis SHALL include product-controlled action counts.
