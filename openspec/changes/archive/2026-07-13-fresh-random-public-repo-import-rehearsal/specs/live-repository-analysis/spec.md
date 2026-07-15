## ADDED Requirements

### Requirement: Public import validates optional global credentials
The live repository analysis flow SHALL allow a configured global GitHub token for public imports and SHALL retry with anonymous public access only when that token receives a 401 or 403 response.

#### Scenario: Valid global token exists during public import
- **WHEN** a public workspace starts a GitHub import with a global token that GitHub accepts
- **THEN** the import SHALL continue using that token for bounded provider access.

#### Scenario: Stale global token exists during public import
- **WHEN** a public workspace validates an optional global token and GitHub returns 401 or 403
- **THEN** the import SHALL retry with bounded anonymous public access instead of failing because the optional credential is unauthorized.

#### Scenario: Owner-scoped token-backed repository imports
- **WHEN** a workspace is explicitly bound to an owner-scoped GitHub token access source
- **THEN** the import SHALL continue using that bound token and SHALL NOT fall back to anonymous public access.

#### Scenario: Installation-backed repository imports
- **WHEN** a workspace is explicitly installation-backed
- **THEN** the import SHALL preserve the installation-backed credential path rather than treating the workspace as anonymous public access.