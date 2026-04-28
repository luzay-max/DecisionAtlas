## ADDED Requirements

### Requirement: GitHub App sync operations are product-observable
The system SHALL expose GitHub App-backed sync provenance in product-facing summaries so users can distinguish manual full import, manual incremental sync, installation-backed sync, and webhook-triggered sync.

#### Scenario: Latest sync origin is labeled for users
- **WHEN** a workspace has a latest import or sync with a recorded sync origin
- **THEN** the product SHALL display a user-readable sync origin label rather than exposing only the raw internal value

#### Scenario: Webhook sync is visually distinct from manual sync
- **WHEN** the latest or active sync was triggered by a GitHub webhook
- **THEN** the product SHALL describe it as webhook-triggered incremental sync and SHALL NOT present it as a manual rerun

#### Scenario: Installation-backed sync source remains visible
- **WHEN** a workspace is backed by a GitHub App installation access source
- **THEN** the product SHALL show the GitHub App access-source label alongside sync provenance on workspace or import surfaces

### Requirement: GitHub App webhook operations have operator validation guidance
The system SHALL document how an operator configures, validates, and troubleshoots GitHub App webhook-triggered sync without requiring live credentials in default CI.

#### Scenario: Operator validates webhook configuration
- **WHEN** an operator prepares a GitHub App-backed environment
- **THEN** documentation SHALL identify the required webhook endpoint, event type expectations, secret boundary, and a bounded validation path

#### Scenario: Operator can troubleshoot unresolved webhook events
- **WHEN** webhook delivery does not enqueue an incremental sync
- **THEN** documentation SHALL describe likely causes such as missing installation binding, unmatched repository, invalid headers or signature, duplicate active sync, and provider/network failure

#### Scenario: CI remains deterministic
- **WHEN** release validation runs in default CI or local pre-release mode
- **THEN** webhook behavior SHALL be validated through deterministic API/engine tests rather than requiring live GitHub webhook delivery
