# Password Hash Deployment and Rollback Guide

[Operations Runbook](../project/self-hosted-operations-runbook.md) | [Deployment](../project/deployment.md) | [中文部署指南](../project/deployment_zh-CN.md)

---

## Scope

B05 changes the password hash written by DecisionAtlas from the legacy PBKDF2-SHA256 `salt$hex` format to Argon2id PHC strings.

- New accounts, local bootstrap identities, and password resets write Argon2id.
- A legacy PBKDF2 account is upgraded only after a successful password verification during login.
- The verifier accepts both the exact legacy PBKDF2 format and bounded Argon2id PHC parameters.
- The existing `actors.password_hash` TEXT column is reused. B05 does not require a schema migration or an offline bulk rewrite.
- This guide does not authorize production deployment, account migration, #34 schema changes, or #36 worker lifecycle changes.

## Argon2id PHC Resource Bounds

Before invoking the Argon2 verifier, B05 parses the PHC parameters and rejects hashes outside these limits:

| Parameter | Accepted range |
| --- | ---: |
| Argon2 type | Argon2id only |
| PHC version | 19 |
| Memory cost | 8 × parallelism to 65,536 KiB |
| Time cost | 1–4 |
| Parallelism | 1–4 |
| Salt length | 8–64 bytes |
| Derived hash length | 16–64 bytes |

The current writer uses 19,456 KiB, 2 iterations, parallelism 1, a 16-byte salt, and a 32-byte hash. These verifier caps are an explicit resource ceiling, not a promise to accept arbitrary stronger external PHC settings. Revisit the limits deliberately if the writer policy changes or a future import feature is introduced.

## Critical Compatibility Boundary

Compatibility is intentionally asymmetric:

| Application version | Legacy PBKDF2 | Argon2id |
| --- | --- | --- |
| Pre-B05 | Verify | **Cannot verify** |
| B05-compatible dual verifier | Verify | Verify |

The first successful legacy login handled by B05 can write an Argon2id hash. A new account or password reset can do so as well. From that point, a pre-B05 binary may reject that account's correct password because it does not understand the Argon2id format.

**Never perform an application-only rollback to a pre-B05 binary after any Argon2id hash may have been written.**

## Multi-Instance Deployment

Do not run pre-B05 and B05 instances together behind the same login traffic once B05 writes are enabled. A user may be routed to a new instance, have the hash upgraded, and then be routed to an old instance that cannot verify it.

Recommended controlled cutover:

1. Announce the maintenance window and pause new login traffic if required by the deployment topology.
2. Take a protected PostgreSQL backup and verify that the backup is readable. Record the backup identifier, current commit/package version, and time.
3. Drain and stop **all** pre-B05 Engine instances. Confirm no old worker or web process can still route authentication requests to a pre-B05 Engine.
4. Deploy the same B05-compatible release to every Engine instance. Do not reopen traffic while old instances remain.
5. Run health checks and the operator's login/session smoke checks.
6. Restore login traffic. Successful legacy logins will upgrade lazily; accounts that do not log in remain PBKDF2 until a later successful login.
7. Keep the verified backup and the B05-compatible rollback package until post-deployment validation is complete.

If zero-downtime rolling deployment is required, first ship a separate compatibility-only release to every instance that can **verify both formats while still writing PBKDF2**. Only after every instance runs that compatibility release should a later release enable Argon2id writes. Do not assume B05 itself is safe to mix with pre-B05 instances.

## Rollback Rules

If B05 validation fails:

1. Stop or drain authentication traffic and all Engine instances.
2. Prefer rolling back to a release that retains the PBKDF2 + Argon2id dual verifier.
3. Preserve the current database and failure evidence before any recovery action.
4. Restore the pre-deployment database backup only if the operator explicitly chooses to return to a pre-B05 binary and accepts that all data changes after that backup may be lost or require reconciliation.
5. Restart the selected compatible release and verify login, password reset, session revocation, and account-disable behavior.

A database restore to the pre-B05 backup is not a routine application rollback. Do not selectively rewrite or downgrade stored hashes by hand. Do not infer that a transaction rollback test establishes binary rollback compatibility.

## Backup and Recovery Checklist

- [ ] Protected PostgreSQL backup completed and restore readability checked.
- [ ] Current and target application commits recorded.
- [ ] All pre-B05 Engine instances drained before Argon2id writes are enabled.
- [ ] Every active Engine instance runs a dual-verifier release.
- [ ] Login, reset-password, account-disable, and existing-session revocation smoke checks passed.
- [ ] Rollback target is B05-compatible, or a separately approved full database restore plan exists.
- [ ] No production hash rewrite, account reset, or schema migration was performed without separate authorization.

## Test Evidence Boundary

The B05 tests cover hash verification, lazy upgrade, wrong-password behavior, transaction rollback, and coordinated login/reset/disable races on file-backed SQLite and PostgreSQL 17. CI databases are disposable and synthetic. They do not constitute production deployment or production account-migration evidence.
