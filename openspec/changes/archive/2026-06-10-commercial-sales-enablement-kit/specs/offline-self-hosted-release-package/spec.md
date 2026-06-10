## ADDED Requirements

### Requirement: Self-hosted package includes sales enablement materials
The self-hosted release package SHALL include the commercial sales enablement kit.

#### Scenario: Package is built
- **WHEN** a self-hosted package is generated
- **THEN** the package manifest and copied docs MUST include the sales page draft, one-page brief, and use-case materials

#### Scenario: Package verification runs
- **WHEN** offline package verification checks a generated package
- **THEN** it MUST require the sales enablement materials as package files
