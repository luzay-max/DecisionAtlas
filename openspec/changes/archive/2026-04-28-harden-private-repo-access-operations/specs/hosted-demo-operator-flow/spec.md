## ADDED Requirements

### Requirement: Hosted operator guidance covers private access hardening
Hosted operator documentation SHALL describe how to validate and troubleshoot token-backed private repository access without requiring live credentials in default CI.

#### Scenario: Operator validates private access manually
- **WHEN** an operator prepares a hosted preview with private repository access
- **THEN** documentation SHALL identify the setup path, recommended token permission boundary, validation steps, and expected product state

#### Scenario: Operator troubleshoots private access failures
- **WHEN** private repository access fails during lookup, binding, import, sync, or readiness review
- **THEN** documentation SHALL describe likely causes including missing source, unauthorized or revoked token, insufficient permissions, repository not found, provider or network failure, and stale status

#### Scenario: Default CI avoids live private credentials
- **WHEN** release validation runs in default CI or local pre-release mode
- **THEN** private repository access behavior SHALL be validated through deterministic tests rather than requiring live private repository credentials
