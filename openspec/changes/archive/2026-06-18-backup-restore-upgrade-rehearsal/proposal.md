## Why

DecisionAtlas now has a self-hosted package, pilot kit, readiness history, and private-repo evidence template, but backup/restore/upgrade remains mostly a runbook promise. Before customer pilot or paid self-hosted claims, operators need bounded rehearsal evidence that backup custody, restore readiness, upgrade validation, rollback planning, and post-upgrade evidence are explicitly checked.

## What Changes

- Add a backup/restore/upgrade rehearsal capability with JSON and Markdown evidence output.
- Add a local verifier/rehearsal script that checks backup, restore, upgrade, rollback, custody, and post-upgrade evidence inputs without performing destructive database operations.
- Add a safe example rehearsal input template for operator-guided evidence.
- Update self-hosted delivery and commercial baseline guidance to require backup/restore/upgrade rehearsal evidence before clean long-term self-hosted claims.
- Add tests for pass/warning/blocking states and secret/custody boundaries.
- Record real stack, browser, guardrail, and public repo stand-in validation in the update log.

## Capabilities

### New Capabilities

- `backup-restore-upgrade-rehearsal`: Bounded self-hosted operational continuity evidence for backup, restore, upgrade, rollback, and post-upgrade validation.

### Modified Capabilities

- `self-hosted-commercial-baseline`: Customer-facing self-hosted claims must distinguish package readiness from backup/restore/upgrade continuity evidence.
- `self-hosted-delivery-rehearsal`: Delivery rehearsal guidance must include backup/restore/upgrade evidence or preserve missing/operator-guided states.

## Impact

- Adds `scripts/ci/rehearse_backup_restore_upgrade.py`.
- Adds `templates/backup-restore-upgrade-rehearsal.example.json`.
- Adds customer/operator documentation updates under `docs/project/`.
- Adds CI tests under `services/engine/tests/ci/`.
- Updates OpenSpec specs and archived change artifacts.
- No runtime API, database schema, billing, SaaS, or hosted secret-vault changes.
