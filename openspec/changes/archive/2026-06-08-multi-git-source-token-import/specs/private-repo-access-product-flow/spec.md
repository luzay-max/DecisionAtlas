## ADDED Requirements

### Requirement: Private access setup becomes provider-aware
The admin private access setup surface SHALL allow repository access setup to be expressed in provider-aware terms while preserving the existing GitHub token-backed behavior.

#### Scenario: Admin sees provider and access mode
- **WHEN** an admin opens repository access setup
- **THEN** the product SHALL show provider and access-mode fields or labels so the admin understands whether they are configuring public, token, or local-path access

#### Scenario: GitHub token setup still works
- **WHEN** an admin submits a GitHub token-backed setup request
- **THEN** the product SHALL use the existing GitHub private-access binding behavior and show safe provider/access status

#### Scenario: Non-admin cannot manage provider setup
- **WHEN** a reviewer or viewer opens the same surface
- **THEN** the product SHALL hide or disable provider/token/local-path setup controls and explain that admin role is required
