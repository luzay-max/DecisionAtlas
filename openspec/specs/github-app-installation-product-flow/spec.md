## Purpose
Define the product-facing GitHub App installation setup and visibility flow for owner-scoped repository access.

## Requirements
### Requirement: Product exposes GitHub App installation setup
The system SHALL provide an admin-facing product surface for binding a GitHub App installation to a repository inside the current owner scope.

#### Scenario: Admin opens installation setup
- **WHEN** an admin views the live analysis or workspace management surface
- **THEN** the product SHALL expose a GitHub App installation setup entry point for the current owner scope

#### Scenario: Reviewer cannot manage installation setup
- **WHEN** a reviewer or viewer views the same product surface
- **THEN** the product SHALL hide or disable installation setup controls and explain that admin role is required

#### Scenario: Current owner scope is visible during setup
- **WHEN** the installation setup surface is shown
- **THEN** the product SHALL display the current owner scope so the admin knows where the installation will be bound

### Requirement: Admin can bind repository to installation-backed access source
The system SHALL let an admin bind a repository to a GitHub App installation-backed access source by using the existing installation binding API.

#### Scenario: Installation binding succeeds
- **WHEN** an admin submits a repository and installation id for the current owner scope
- **THEN** the product SHALL call the installation binding API and show the resulting access-source label and workspace slug

#### Scenario: Installation binding fails validation
- **WHEN** the installation binding API rejects the repository or installation payload
- **THEN** the product SHALL show a bounded error message without changing the visible workspace state

#### Scenario: Binding keeps session scope as authority
- **WHEN** the product submits installation binding
- **THEN** it SHALL rely on the current authenticated session scope rather than allowing a typed owner-scope override

### Requirement: Installation-backed workspace state is visible
The system SHALL identify installation-backed workspace state in live analysis and workspace surfaces using access-source and sync provenance metadata.

#### Scenario: Lookup finds installation-backed workspace
- **WHEN** repository lookup finds an imported workspace bound through a GitHub App installation
- **THEN** the product SHALL show that installation-backed access-source label before offering open, sync, or rerun actions

#### Scenario: Workspace dashboard shows installation-backed source
- **WHEN** an installation-backed workspace dashboard is shown
- **THEN** the product SHALL display the GitHub App installation access-source label and latest sync provenance when available

#### Scenario: Webhook-triggered sync remains distinguishable
- **WHEN** the latest or active sync came from a GitHub webhook
- **THEN** the product SHALL describe that sync origin distinctly from manual full rerun or manual incremental sync

### Requirement: Installation binding surfaces post-binding sync state
The product SHALL connect successful GitHub App installation binding to the workspace's subsequent sync state so admins can see what the binding enabled after setup.

#### Scenario: Binding result points to installation-backed workspace state
- **WHEN** an admin successfully binds a repository to a GitHub App installation
- **THEN** the product SHALL show the resulting access-source label and workspace identity, and SHALL make it clear that future sync provenance should be viewed from the workspace or import surface

#### Scenario: Existing installation-backed lookup shows sync controls
- **WHEN** repository lookup finds an installation-backed workspace
- **THEN** the product SHALL show the GitHub App access-source label before offering open, full rerun, or incremental sync actions

#### Scenario: Dashboard explains App-backed freshness
- **WHEN** an installation-backed workspace dashboard is rendered
- **THEN** it SHALL display the access-source label and latest or active sync provenance in a way that answers whether the workspace was updated manually or through webhook sync
