## ADDED Requirements

### Requirement: Fresh import rehearsal reports sparse decision conversion
Fresh public repository import rehearsal evidence SHALL include compact sparse-conversion eligibility, attempts, candidate yield, rejection reasons, and residual loss reasons from the terminal import summary.

#### Scenario: Fresh import runs sparse recovery
- **WHEN** a fresh repository import invokes sparse decision recovery
- **THEN** JSON and Markdown evidence SHALL report the bounded attempt count, selected evidence families, recovered candidate count, and resulting core-loop status.

#### Scenario: Fresh import still produces zero candidates
- **WHEN** sparse recovery completes without a grounded candidate
- **THEN** the rehearsal SHALL preserve zero-candidate and `evidence_limited` states
- **AND** it SHALL NOT report the workspace as having an accepted baseline.
