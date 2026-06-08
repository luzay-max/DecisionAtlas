## ADDED Requirements

### Requirement: Live analysis setup is Git-source aware
The live-analysis setup flow SHALL preserve provider and access-mode context when resolving repository lookup, credential setup, import, reuse, sync, and rerun actions.

#### Scenario: GitHub token-backed source is imported
- **WHEN** an admin has bound a GitHub repository to a token-backed access source
- **THEN** live analysis SHALL resolve import or reuse through that source and report provider `github` plus access mode `token`

#### Scenario: Unsupported provider is selected
- **WHEN** an admin selects GitLab or Gitee before full ingestion support exists
- **THEN** live analysis SHALL return an explicit provider setup limitation rather than trying a GitHub import path

#### Scenario: Local path is selected
- **WHEN** an admin selects local-path import
- **THEN** live analysis SHALL treat the source as server-operator-guided and SHALL NOT expose arbitrary server path details to non-admin users
