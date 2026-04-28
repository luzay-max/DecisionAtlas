# v0-3-real-stack-validation Specification

## Purpose
TBD - created by archiving change validate-v0-3-real-stack-flow. Update Purpose after archive.
## Requirements
### Requirement: v0.3 real-stack validation records a reproducible matrix
The system SHALL define a v0.3 real-stack validation matrix that records the command or operator action, observed result, status, known limitation, and follow-up for each product lane being validated.

#### Scenario: Validation report records command evidence
- **WHEN** a maintainer validates a v0.3 product lane
- **THEN** the validation report SHALL record the command or action used, the observed result, and whether the lane passed, failed as blocking, failed as non-blocking, or remains a known limitation

#### Scenario: Validation report is reproducible
- **WHEN** another maintainer reads the validation report
- **THEN** the report SHALL include enough command, environment, and cleanup information to rerun the same validation path without relying on hidden session knowledge

### Requirement: v0.3 real-stack validation covers current product lanes
The system SHALL validate the current v0.3 product lanes across seeded demo, real local stack, public repository import, authenticated scope behavior, GitHub App binding, private repository access binding, hosted operator checks, and canonical release validation.

#### Scenario: Seeded demo lane is validated
- **WHEN** the v0.3 real-stack validation matrix is executed
- **THEN** it SHALL include the seeded demo workspace, review path, why path, drift path, and reset or reseed recovery path where applicable

#### Scenario: Real local stack is validated
- **WHEN** the v0.3 real-stack validation matrix is executed
- **THEN** it SHALL include the real Postgres or Redis stack startup, migrations, seed behavior, API health, engine health, and web access checks

#### Scenario: Public repository import lane is validated
- **WHEN** the v0.3 real-stack validation matrix is executed
- **THEN** it SHALL include lookup, import, dashboard readiness, and sync or reuse behavior for an imported public repository

#### Scenario: Platform access lanes are validated
- **WHEN** the v0.3 real-stack validation matrix is executed
- **THEN** it SHALL include session recovery, owner scope switching, role-gated actions, GitHub App binding surface behavior, and private repository access binding surface behavior

#### Scenario: Operator checks and release gate are validated
- **WHEN** the v0.3 real-stack validation matrix is executed
- **THEN** it SHALL include hosted health checks, hosted smoke checks when an environment is available, and the canonical pre-release validation command

### Requirement: v0.3 real-stack validation separates required and optional checks
The system SHALL distinguish deterministic local checks from optional provider-dependent or credential-dependent checks so default validation remains reliable while live confidence checks remain visible.

#### Scenario: Provider-dependent checks are marked optional
- **WHEN** a validation path requires live provider access, private repository credentials, or GitHub App production configuration
- **THEN** the report SHALL mark that path as operator-guided or optional rather than treating it as a mandatory default CI requirement

#### Scenario: Blocking failures are separated from known limitations
- **WHEN** a validation path does not pass
- **THEN** the report SHALL classify the issue as blocking, non-blocking, or known limitation with a short rationale

#### Scenario: Follow-up work is assigned without scope expansion
- **WHEN** validation reveals a non-blocking product gap
- **THEN** the report SHALL identify the likely follow-up change area without implementing unrelated feature expansion inside the validation change

