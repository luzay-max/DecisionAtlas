## ADDED Requirements

### Requirement: Readiness preserves private access-source status safely
Imported-workspace readiness summaries SHALL preserve token-backed access-source state without exposing credential material.

#### Scenario: Readiness includes private source status
- **WHEN** an imported workspace is bound to a token-backed private access source
- **THEN** the readiness summary SHALL include access-source label, authorization status, and bounded detail when available

#### Scenario: Readiness omits raw private token
- **WHEN** readiness data is returned for a token-backed workspace
- **THEN** the readiness summary SHALL NOT include raw token values or other credential material

#### Scenario: Readiness uses actionable private access copy
- **WHEN** a token-backed workspace has missing, unauthorized, or provider-failure access state
- **THEN** the readiness summary SHALL expose enough bounded context for the product to recommend setup, rotation, retry, or operator investigation
