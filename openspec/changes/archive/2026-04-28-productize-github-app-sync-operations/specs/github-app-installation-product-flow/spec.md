## ADDED Requirements

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
