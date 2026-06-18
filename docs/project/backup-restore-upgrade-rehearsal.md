# Backup Restore Upgrade Rehearsal

[Home](../../README.md) | [Operations Runbook](self-hosted-operations-runbook.md) | [Self-Hosted Delivery Rehearsal](self-hosted-delivery-rehearsal.md) | [Commercial Baseline](self-hosted-commercial-baseline.md)

---

Use this rehearsal before claiming long-term self-hosted continuity readiness for a customer trial, paid pilot, or enterprise handoff.

This rehearsal is intentionally non-destructive. It does not run `pg_dump`, restore PostgreSQL, mutate Redis, apply migrations, upgrade services, or rollback a deployment. It verifies that operator-provided backup, restore, upgrade, rollback, custody, and handoff evidence is explicit and safe to share.

## Evidence Boundary

The committed sample is `operator_guided`. It is not proof that a real customer backup, restore, upgrade, or rollback has been completed.

Real continuity proof must be generated on the operator-controlled or customer-controlled host. Do not commit:

- database dumps
- `.env` files
- provider keys
- repository tokens
- customer identifiers
- raw private source content
- raw local-only logs that expose secrets or infrastructure details

## Required Continuity Lanes

| Lane | Meaning |
| --- | --- |
| `database_backup` | PostgreSQL backup exists or operator action is explicitly pending. |
| `environment_backup` | `.env` and credential custody backup is addressed outside source control. |
| `restore_plan` | Restore order and target revision are documented. |
| `restore_validation` | Real restore validation is attached, or absence is explicit. |
| `upgrade_plan` | Upgrade order, manifest review, and migration intent are documented. |
| `post_upgrade_validation` | Health/readiness/browser/evidence checks after upgrade are attached, or absence is explicit. |
| `rollback_plan` | Rollback decision and failed-upgrade evidence preservation are documented. |
| `handoff_evidence` | Reviewed continuity evidence is ready for readiness history or customer handoff. |

## Command

```powershell
python scripts\ci\rehearse_backup_restore_upgrade.py `
  --input-json templates\backup-restore-upgrade-rehearsal.example.json `
  --output-json .tmp\backup-restore-upgrade-rehearsal.json `
  --output-markdown .tmp\backup-restore-upgrade-rehearsal.md
```

## Status Rules

- `pass`: Evidence supports the lane.
- `warning`: Evidence is usable with disclosure.
- `blocking`: Do not claim continuity readiness until fixed or explicitly excluded.
- `operator_guided`: A human operator must perform or confirm the step.
- `known_limitation`: Current environment cannot validate the step; rerun condition is known.
- `not_provided`: Optional or external evidence was omitted and must not be treated as pass.

## Customer Handoff Rule

Customer-facing continuity claims must reference the generated JSON/Markdown rehearsal evidence or say that it is missing, operator-guided, known-limited, or not provided. Do not describe package readiness as backup/restore/upgrade readiness unless this evidence exists and is reviewed.
