## ADDED Requirements

### Requirement: Benchmark comparison status is derived from bounded metrics
Release rehearsal SHALL derive benchmark comparison lane status from bounded comparison metrics when the source comparison has no explicit top-level status.

#### Scenario: Comparison is release-ready
- **WHEN** benchmark comparison evidence has no explicit status, `release_evidence_ready=true`, zero regressions, and zero operational blockers
- **THEN** release rehearsal SHALL classify the benchmark comparison lane as `pass` rather than `unknown`.

#### Scenario: Comparison is not release-ready
- **WHEN** benchmark comparison evidence has regressions, operational blockers, or does not indicate release evidence readiness
- **THEN** release rehearsal SHALL keep the benchmark comparison lane warning or blocking according to the bounded metrics.
