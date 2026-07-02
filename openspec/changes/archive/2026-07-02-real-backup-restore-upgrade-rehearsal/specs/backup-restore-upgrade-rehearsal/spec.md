## ADDED Requirements

### Requirement: Non-destructive continuity verifier distinguishes real rehearsal evidence
The backup/restore/upgrade verifier SHALL distinguish operator-submitted non-destructive evidence from real scratch-environment continuity rehearsal evidence.

#### Scenario: Real rehearsal evidence is absent
- **WHEN** only non-destructive continuity evidence is available
- **THEN** reports SHALL preserve the verifier status but SHALL NOT claim that backup, restore, upgrade, or rollback mechanics have been exercised

#### Scenario: Real rehearsal evidence is referenced
- **WHEN** real backup/restore/upgrade rehearsal evidence is supplied
- **THEN** the verifier or documentation SHALL reference the real rehearsal status, scratch scope, restore validation result, upgrade lane status, and limitations without copying raw backup content
