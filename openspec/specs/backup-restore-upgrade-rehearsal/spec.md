# backup-restore-upgrade-rehearsal Specification

## Purpose
Define bounded, non-destructive evidence for self-hosted backup, restore, upgrade, rollback, and customer handoff continuity claims.

## Requirements
### Requirement: Backup restore upgrade rehearsal produces bounded evidence
The system SHALL provide a backup/restore/upgrade rehearsal that emits machine-readable JSON and operator-readable Markdown evidence without performing destructive database or rollback operations.

#### Scenario: Operator-guided rehearsal is generated
- **WHEN** an operator provides rehearsal input with backup, restore, upgrade, rollback, custody, and post-upgrade validation lanes
- **THEN** the rehearsal SHALL emit JSON and Markdown evidence that preserves each lane status and summarizes blockers, warnings, limitations, and recommended next actions.

#### Scenario: Real restore evidence is absent
- **WHEN** the rehearsal input does not include completed real restore or upgrade evidence
- **THEN** the rehearsal SHALL preserve `operator_guided`, `known_limitation`, or `not_provided` status rather than claiming a clean pass.

### Requirement: Backup restore upgrade rehearsal validates continuity lanes
The rehearsal SHALL require explicit continuity lanes for database backup, environment/credential backup, restore plan, restore validation, upgrade plan, post-upgrade validation, rollback plan, and evidence handoff.

#### Scenario: Required lane is missing
- **WHEN** a required continuity lane is absent from the rehearsal input
- **THEN** the rehearsal SHALL emit status `blocking` and identify the missing lane.

#### Scenario: Lane status is invalid
- **WHEN** a continuity lane uses an unrecognized status
- **THEN** the rehearsal SHALL emit status `blocking` and identify the invalid lane status.

### Requirement: Backup restore upgrade rehearsal protects sensitive material
The rehearsal SHALL reject obvious sensitive material in input or Markdown evidence, including token-like values, provider key markers, `.env` secret assignments, private key markers, and raw backup contents.

#### Scenario: Secret-like value is detected
- **WHEN** the rehearsal input or Markdown evidence includes obvious token, provider key, private key, or raw secret marker material
- **THEN** the rehearsal SHALL emit status `blocking` without echoing the sensitive value.

#### Scenario: Custody statement is present
- **WHEN** rehearsal evidence is generated
- **THEN** it SHALL state that backups, `.env`, provider keys, repository tokens, and customer-specific artifacts remain under operator or customer control.

### Requirement: Backup restore upgrade rehearsal integrates with handoff evidence
The rehearsal SHALL be usable as bounded evidence for self-hosted delivery, readiness history, and customer handoff workflows.

#### Scenario: Handoff references continuity evidence
- **WHEN** a self-hosted customer handoff claims long-term operability, upgrade readiness, or rollback readiness
- **THEN** the handoff SHALL reference backup/restore/upgrade rehearsal evidence or disclose that the evidence is missing or operator-guided.
