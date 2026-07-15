## ADDED Requirements

### Requirement: Warning reduction honors quality action counts
Random repo warning-lane reduction SHALL use core-loop and multi-repo action category counts when classifying aggregate warning lanes.

#### Scenario: Operator/setup actions dominate
- **WHEN** a multi-repo diagnosis lane reports operator/setup actions and no blocking state
- **THEN** the warning reducer SHALL classify that aggregate warning as operator-guided unless product-controlled action count is clearly present.

#### Scenario: Product actions are present
- **WHEN** a multi-repo diagnosis lane reports product-controlled action counts
- **THEN** the warning reducer SHALL keep product-controlled reduction actions visible and prioritized.
