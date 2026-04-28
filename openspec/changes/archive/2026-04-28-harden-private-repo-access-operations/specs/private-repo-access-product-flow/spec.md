## ADDED Requirements

### Requirement: Private access product surfaces show actionable source state
The product SHALL show token-backed private repository access-source state consistently before users choose open, sync, rerun, or troubleshooting actions.

#### Scenario: Lookup shows token-backed state before actions
- **WHEN** repository lookup finds a token-backed private workspace in the current owner scope
- **THEN** the product SHALL show access-source label, authorization status, and bounded authorization detail before open, sync, or rerun actions

#### Scenario: Dashboard shows token-backed operational state
- **WHEN** a token-backed private workspace dashboard is rendered
- **THEN** the product SHALL show the private access-source label, authorization status, and safe detail when available

#### Scenario: Private access setup explains recovery
- **WHEN** private access binding fails because credentials are missing, unauthorized, invalid, or cannot reach the repository
- **THEN** the product SHALL display a bounded recovery-oriented message without rendering the submitted token

### Requirement: Private access setup documents current security boundary
The product and operator documentation SHALL explain the current token-backed private access boundary.

#### Scenario: Admin sees token handling boundary
- **WHEN** an admin opens private access setup
- **THEN** the product or linked documentation SHALL explain that tokens are used to create an owner-scoped access source and are not echoed back after submission

#### Scenario: Operator sees supported token guidance
- **WHEN** hosted-preview documentation describes private repository access
- **THEN** it SHALL include recommended minimum permissions, rotation guidance, troubleshooting steps, and explicit non-goals such as no secret vault or OAuth self-service
