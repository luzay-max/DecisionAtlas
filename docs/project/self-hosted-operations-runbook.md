# Self-Hosted Operations Runbook

[Home](../../README.md) | [Package Guide](self-hosted-package-guide.md) | [Deployment](deployment.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Continuity Rehearsal](backup-restore-upgrade-rehearsal.md) | [Password Hash Upgrade and Rollback](../security/password-hash-deployment-rollback.md)

---

This runbook defines first setup, backup, restore, upgrade, and rollback expectations for a DecisionAtlas self-hosted package.

## First Setup

1. Prepare PostgreSQL and Redis on the customer-controlled server.
2. Copy `templates/self-hosted.env.example` to `.env`.
3. Fill `DATABASE_URL`, `REDIS_URL`, `ENGINE_BASE_URL`, and `API_BASE_URL`.
4. Keep `APP_ENV=production` and `AUTO_BOOTSTRAP_AUTH=false`; set `CORS_ALLOWED_ORIGINS` to the exact public Web origin(s), never `*`.
5. Configure optional provider keys only on backend/server-side surfaces.
6. Start DecisionAtlas with the package startup scripts.
7. Confirm Web, API, and Engine health.
8. Initialize the first admin account using the deployment-specific admin flow; do not enable anonymous API bootstrap on a public deployment.
9. Run readiness checks before inviting reviewer or viewer users.
10. For paid pilots or customer delivery, prepare a private entitlement record from `templates/self-hosted-entitlement.example.json`.

## First Admin Boundary

DecisionAtlas Team Self-hosted assumes administrator-managed accounts in this stage. The first admin is responsible for:

- creating reviewer and viewer accounts
- assigning workspace permissions
- configuring repository access tokens or installation bindings
- running import and readiness evidence commands
- preserving `.env` and credential backups outside source control

Self-service signup, password recovery, enterprise SSO, and hosted account operations are out of scope for this package.

## Backup

Before customer evaluation, upgrade, or risky maintenance:

- Back up PostgreSQL using the operator's normal database backup process.
- Back up `.env` and any credential files outside source control.
- Record the DecisionAtlas commit or package version label.
- Record current readiness evidence output if available.
- Treat Redis as recoverable runtime/cache state unless the deployment has explicitly chosen to persist queue state differently.

Minimum PostgreSQL example:

```powershell
pg_dump $env:DATABASE_URL > decisionatlas-backup.sql
```

Use customer-approved backup tooling for production or private deployments.

Before customer handoff, generate bounded continuity evidence:

```powershell
python scripts\ci\rehearse_backup_restore_upgrade.py `
  --input-json templates\backup-restore-upgrade-rehearsal.example.json `
  --output-json .tmp\backup-restore-upgrade-rehearsal.json `
  --output-markdown .tmp\backup-restore-upgrade-rehearsal.md
```

The rehearsal is non-destructive. It checks that backup, restore, upgrade, rollback, custody, and post-upgrade validation evidence is explicit; it does not prove a real restore unless operator-supplied restore evidence is attached.

## Restore

Restore order:

1. Stop Web, API, and Engine.
2. Restore PostgreSQL from the selected backup.
3. Restore `.env` and credential files from the secure operator backup location.
4. Start PostgreSQL and Redis.
5. Start DecisionAtlas services.
6. Run migrations only for the intended target revision.
7. Run health checks and readiness checks.
8. Confirm imported workspaces, team accounts, and audit history are visible.

Seeded demo reset/reseed scripts are scoped to demo readiness. They must not be treated as imported workspace recovery.

## Upgrade

Upgrade order:

1. Record current package version, commit, and evidence state.
2. Back up PostgreSQL and `.env`.
3. Unpack or deploy the new package revision.
4. Review `manifest.json` and release notes.
5. Apply environment template changes manually; never overwrite live secrets blindly.
6. Start services and run migrations.
7. Run package verification, OpenSpec validation, pre-release checks, and readiness evidence.
8. Run browser/operator smoke for team workflow and critical review/drift flows.
9. Generate a team handoff report from release evidence, hosted readiness, benchmark comparison, package verification, and readiness history before external delivery.
10. Run clean self-hosted install rehearsal against the package copy and attach `.tmp/clean-self-hosted-install-rehearsal.json/md`.
11. Attach or explicitly defer license/support boundary evidence before claiming a paid customer handoff.

## Password Hash Upgrade (B05)

B05 writes Argon2id password hashes for new accounts, password resets, and successful legacy PBKDF2 logins. The existing `actors.password_hash` column is reused; there is no schema migration or offline bulk rewrite.

Before deploying a B05-compatible release:

- Take and verify a protected PostgreSQL backup.
- Record the exact application commit/package version.
- Plan a maintenance window or a coordinated all-instance cutover. Do not leave pre-B05 and B05 instances serving login traffic together once any B05 instance can write Argon2id hashes.
- Drain/stop all pre-B05 Engine instances, deploy the dual-verifier B05-compatible release to every instance, run health/readiness checks, then restore traffic.
- Keep the database backup and rollback target available until post-deployment validation is complete.

**Rollback compatibility is asymmetric:** B05 verifies both legacy PBKDF2 and Argon2id, but a pre-B05 binary verifies only PBKDF2. After the first Argon2id hash is written, do not roll back only the application binary to pre-B05. The safe application rollback target must retain dual-format verification. Returning to a pre-B05 binary would require restoring a complete database backup taken before the first Argon2id write and explicitly accepting/reconciling all data loss since that backup; do not use that as an automatic rollback.

The login transaction rollback test proves a failed login cannot partially persist its hash upgrade or session. It does **not** prove that a pre-B05 binary can read Argon2id hashes. See the [password hash deployment and rollback guide](../security/password-hash-deployment-rollback.md) for the release sequence and recovery checklist.

## Rollback

If upgrade validation fails:

1. Stop services.
2. Restore the previous app revision or package.
3. Restore PostgreSQL backup if migrations or data writes must be reverted.
4. Restore previous `.env` if changed.
5. Start services.
6. Rerun health/readiness checks.
7. Record the failed upgrade evidence and follow-up actions.

Rollback is a human operator decision. The package verifier does not perform rollback automatically.

## Clean Install Rehearsal

Use clean install rehearsal when validating that the package can be understood and inspected outside the live development tree:

```powershell
python scripts\ci\rehearse_clean_self_hosted_install.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --team-handoff-json .tmp\team-handoff-report.json
```

If live Web/API/Engine URLs are not provided, the report must keep live stack probing as `operator_guided` or `not_provided`. Do not treat clean package copy checks as proof that a customer server has already started successfully.
