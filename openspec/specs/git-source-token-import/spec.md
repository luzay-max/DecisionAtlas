## Purpose
Define provider-aware Git source access setup, token safety, and bounded setup outcomes for self-hosted repository import flows.

## Requirements

### Requirement: Git source setup is provider-aware
The system SHALL represent repository access setup with provider, access mode, repository identifier, owner scope, credential reference, workspace slug, authorization status, and bounded setup outcome.

#### Scenario: Admin configures GitHub token source
- **WHEN** an admin submits a GitHub repository identifier and token for the current owner scope
- **THEN** the system SHALL bind the repository to a token-backed GitHub access source, return provider/access-mode metadata, and omit raw token material from the response

#### Scenario: Admin configures unsupported provider
- **WHEN** an admin submits a GitLab or Gitee repository source before full provider ingestion is implemented
- **THEN** the system SHALL return a bounded not-yet-implemented or operator-guided setup outcome rather than a generic import failure

#### Scenario: Admin configures local path source
- **WHEN** an admin submits a local repository path source
- **THEN** the system SHALL classify it as server-side local-path setup and SHALL NOT allow non-admin users to configure or inspect sensitive path setup details

### Requirement: Git source tokens remain write-only
The system SHALL accept token material only through admin-authorized setup actions and SHALL NOT expose token values in API responses, UI state, evidence, logs intended for release history, or readiness output.

#### Scenario: Token setup response omits token
- **WHEN** token-backed setup succeeds or fails
- **THEN** the response SHALL include provider, access mode, authorization status, and bounded detail without including the submitted token

#### Scenario: Reviewer cannot configure token
- **WHEN** a reviewer or viewer attempts token-backed setup
- **THEN** the system SHALL reject the action or hide the setup control and SHALL NOT persist submitted credential material

### Requirement: Git source setup reports bounded outcomes
The system SHALL report Git source setup outcomes using bounded categories that distinguish success, credential required, unauthorized, repository not found, rate limited, network failure, provider unsupported, local path unavailable, and operator-guided setup.

#### Scenario: GitHub token is unauthorized
- **WHEN** GitHub rejects a submitted token
- **THEN** the system SHALL report an authorization-specific outcome without echoing the token

#### Scenario: Provider is unsupported
- **WHEN** a provider is recognized but ingestion is not implemented
- **THEN** the system SHALL report `provider_unsupported` or an equivalent bounded setup outcome with a next action for operator planning

#### Scenario: Local path is unavailable
- **WHEN** a local repository path cannot be validated by the server-side operator environment
- **THEN** the system SHALL report `local_path_unavailable` or an equivalent bounded setup outcome instead of treating it as a provider network failure
