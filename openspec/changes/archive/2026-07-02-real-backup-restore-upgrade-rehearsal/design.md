## Context

The current continuity flow is intentionally non-destructive: `rehearse_backup_restore_upgrade.py` validates operator-submitted evidence and prevents raw backups or secrets from entering committed artifacts. That is safe, but it does not prove a backup can be restored or that post-upgrade checks can run against restored state.

The next commercial gap is a real rehearsal that operates on explicit scratch resources only. It should never touch production databases, customer backups, live `.env` files, or private source content. The first implementation should be deterministic enough for CI/local validation and honest enough for customer handoff.

## Goals / Non-Goals

**Goals:**

- Provide a real continuity rehearsal that can create a bounded backup artifact from scratch state, restore it into a separate scratch target, and validate expected records/counts.
- Record package/version transition metadata and post-upgrade validation evidence without claiming full production migration coverage.
- Generate JSON and Markdown evidence that downstream delivery, handoff, and audit reports can summarize.
- Enforce path safety and custody boundaries so the rehearsal cannot accidentally operate outside the intended scratch root.
- Keep missing external/customer continuity evidence explicit.

**Non-Goals:**

- Operate on production customer databases.
- Store raw database dumps, `.env` files, provider keys, repository tokens, or private repository content in committed artifacts.
- Implement automated cloud provisioning, live customer rollback, or destructive upgrade orchestration.
- Replace the existing non-destructive verifier; both evidence layers remain useful.
- Add billing, SaaS multi-tenancy, hosted secret vault, online license enforcement, or enterprise SSO.

## Decisions

1. Use scratch-only inputs.

   Rationale: the rehearsal should be safe by construction. It should require explicit scratch paths and refuse paths outside an owned `.tmp` rehearsal root.

   Alternative considered: allow arbitrary database URLs and backup paths. Rejected because it risks touching production-like state and makes CI unsafe.

2. Separate real rehearsal evidence from non-destructive verifier evidence.

   Rationale: the existing verifier is good for customer/operator-submitted evidence. The new rehearsal proves local/scratch mechanics. Reports should show both honestly.

   Alternative considered: mutate the existing verifier into a real runner. Rejected because it would blur safety guarantees and break existing docs/tests.

3. Prefer deterministic seed/restore checks before full service orchestration.

   Rationale: the first real proof should verify backup/restore data integrity reliably. Full Web/API/Engine post-upgrade smoke can be optional or attached as source evidence.

   Alternative considered: require the full stack for every rehearsal. Rejected because local CI and clean package validation would become fragile.

4. Generate evidence by reference.

   Rationale: downstream reports should summarize status, counts, paths, and limitations without embedding raw backup content or logs.

   Alternative considered: copy backup/restore logs into handoff and audit reports. Rejected because logs can leak paths or secrets.

## Risks / Trade-offs

- [Risk] Scratch rehearsal could be mistaken for production readiness -> Mitigation: evidence must say scratch-only unless external/customer evidence is supplied.
- [Risk] Path safety bugs could delete or overwrite wrong data -> Mitigation: refuse destructive operations outside an owned scratch root and test that boundary.
- [Risk] Database tooling differs by environment -> Mitigation: start with JSON/SQLite-style deterministic scratch fixtures or explicit dry-run adapters, then allow Postgres commands only when provided and bounded.
- [Risk] Upgrade evidence becomes too broad -> Mitigation: define package/version transition and post-upgrade validation as bounded lanes, not full automatic upgrade management.

## Migration Plan

1. Add the real rehearsal script and scratch evidence format.
2. Add tests for pass, missing inputs, unsafe paths, restore mismatch, and downstream summary.
3. Update docs and package/readiness report generators to accept optional real continuity evidence.
4. Run targeted Python tests and OpenSpec strict validation.
5. Record implementation and validation evidence in the update log.

Rollback is low risk: remove the new script, optional input flags, and delta spec additions. Existing non-destructive backup/restore/upgrade verifier remains compatible.

## Open Questions

- Should the first real rehearsal use a lightweight JSON/SQLite scratch fixture, a Postgres-only path, or support both?
- Should live Web/API/Engine smoke be required for `pass`, or remain an attachable optional source evidence lane?
- Should real continuity evidence be archived into readiness history automatically, or only referenced by handoff/audit reports?
