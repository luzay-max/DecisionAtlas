# real-backup-restore-upgrade-rehearsal Specification

## Purpose
Define scratch-only real backup, restore, upgrade, rollback, and continuity evidence generation for DecisionAtlas self-hosted package delivery.

## Requirements

### Requirement: Real continuity rehearsal uses scratch-only resources
The system SHALL run real backup/restore/upgrade rehearsal operations only against explicit scratch resources.

#### Scenario: Scratch rehearsal starts
- **WHEN** an operator runs the real backup/restore/upgrade rehearsal with a label and scratch root
- **THEN** the system SHALL create or use a label-scoped scratch workspace and SHALL record the scratch source, backup artifact, restore target, and evidence output paths

#### Scenario: Unsafe path is rejected
- **WHEN** a requested source, backup, restore, or working path resolves outside the owned scratch root
- **THEN** the rehearsal SHALL stop with `blocking` evidence and SHALL NOT delete, overwrite, or mutate that path

### Requirement: Real continuity rehearsal validates backup and restore integrity
The system SHALL verify that scratch source state can be backed up and restored into a separate scratch target.

#### Scenario: Restore matches expected state
- **WHEN** scratch source state is backed up and restored
- **THEN** the rehearsal SHALL compare expected records, checksums, or count summaries and SHALL mark restore validation `pass` only when the restored state matches expectations

#### Scenario: Restore mismatch is detected
- **WHEN** restored state differs from expected source state
- **THEN** the rehearsal SHALL mark restore validation `blocking` or `warning` and SHALL include bounded mismatch details without embedding raw backup content

### Requirement: Real continuity rehearsal records upgrade and rollback evidence
The system SHALL record bounded upgrade and rollback readiness evidence for the scratch rehearsal.

#### Scenario: Upgrade evidence is supplied
- **WHEN** package/version transition metadata and post-upgrade validation evidence are supplied or generated
- **THEN** the rehearsal SHALL record previous version, target version, post-upgrade status, rollback plan status, limitations, and recommended next actions

#### Scenario: Upgrade evidence is missing
- **WHEN** post-upgrade validation or rollback plan evidence is not provided
- **THEN** the rehearsal SHALL preserve `operator_guided`, `not_provided`, or `known_limitation` and SHALL NOT claim clean upgrade readiness

### Requirement: Real continuity rehearsal emits customer-safe evidence
The system SHALL emit JSON and Markdown continuity evidence without exposing secrets, raw backups, raw `.env`, private repository content, or unbounded local logs.

#### Scenario: Evidence is generated
- **WHEN** the real continuity rehearsal completes or pauses
- **THEN** it SHALL write JSON and Markdown evidence containing schema version, generated timestamp, label, status, scratch resource summary, lane statuses, blockers, limitations, custody note, and recommended next actions

#### Scenario: Sensitive material is detected
- **WHEN** generated evidence or operator-provided evidence contains token-like values, `.env` secret assignments, database URLs with credentials, private key markers, raw backup markers, or raw private repository snippets
- **THEN** the rehearsal SHALL mark evidence `blocking` or fail with a bounded redaction error without copying the sensitive value into Markdown
