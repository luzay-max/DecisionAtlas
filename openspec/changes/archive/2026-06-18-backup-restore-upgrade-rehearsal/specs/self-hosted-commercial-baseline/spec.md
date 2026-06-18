## ADDED Requirements

### Requirement: Self-hosted commercial baseline distinguishes continuity readiness
The self-hosted commercial baseline SHALL distinguish deployable package readiness from backup, restore, upgrade, and rollback continuity readiness.

#### Scenario: Commercial claim references long-term operation
- **WHEN** documentation, sales material, release notes, or customer handoff claims long-term self-hosted operation readiness
- **THEN** it SHALL reference backup/restore/upgrade rehearsal evidence or disclose that continuity evidence remains missing, operator-guided, or known-limited.

#### Scenario: Continuity evidence is incomplete
- **WHEN** backup, restore, upgrade, or rollback rehearsal evidence is incomplete
- **THEN** the commercial baseline SHALL prevent clean continuity claims and require the limitation to remain visible.
