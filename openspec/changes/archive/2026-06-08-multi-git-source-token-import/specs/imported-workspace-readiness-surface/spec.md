## ADDED Requirements

### Requirement: Imported readiness includes Git source metadata
Imported-workspace readiness summaries SHALL include safe Git source metadata such as provider, access mode, access-source label, authorization status, and setup outcome without exposing credential material.

#### Scenario: GitHub token-backed readiness is shown
- **WHEN** a token-backed GitHub workspace readiness summary is returned
- **THEN** the summary SHALL include provider `github`, access mode `token`, authorization status, and safe detail without exposing the token

#### Scenario: Unsupported provider readiness is shown
- **WHEN** a workspace or setup attempt is associated with a recognized but unsupported provider
- **THEN** readiness SHALL expose a bounded provider limitation and next action instead of implying that analysis failed

#### Scenario: Local path readiness is shown
- **WHEN** a workspace or setup attempt is associated with local-path access
- **THEN** readiness SHALL expose safe local-path setup status without rendering sensitive server path details to users without admin role
