## ADDED Requirements

### Requirement: Product-managed private access sources avoid raw credential exposure
The system SHALL allow product-managed private repository access setup while keeping raw credential material out of workspace records and product result surfaces.

#### Scenario: Private access source is created from product setup
- **WHEN** an admin submits private repository access credentials through the product
- **THEN** the platform SHALL create or update the owner-scoped access-source record and bind the workspace to that source without storing raw credential material on the workspace

#### Scenario: Product result omits submitted credential
- **WHEN** private access setup returns a workspace or access-source result
- **THEN** the result SHALL include source label and authorization state but SHALL NOT include the submitted token value

#### Scenario: Rebinding preserves source status semantics
- **WHEN** an admin rebinds a repository to an existing token-backed source reference
- **THEN** the platform SHALL preserve the access-source status model so workspace surfaces can still report authorized, missing, or unauthorized source state
