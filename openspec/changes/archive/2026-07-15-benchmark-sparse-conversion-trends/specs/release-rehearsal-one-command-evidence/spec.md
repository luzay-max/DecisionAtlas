## MODIFIED Requirements

### Requirement: Release rehearsal preserves mixed outcomes
The release rehearsal SHALL aggregate release, hosted, benchmark comparison, sparse benchmark trend, multi-repo diagnosis, guardrail, and history lane outcomes without hiding warnings or blockers.

#### Scenario: A lane is warning
- **WHEN** release, hosted readiness, benchmark trend, sparse benchmark trend, multi-repo diagnosis, guardrail, or history evidence reports warning
- **THEN** the top-level rehearsal status SHALL be warning unless a blocking lane exists.

#### Scenario: A lane is blocking
- **WHEN** any included lane reports blocking, provider failure, local stack failure, or command failure
- **THEN** the top-level rehearsal status SHALL be blocking and include recommended follow-up.
