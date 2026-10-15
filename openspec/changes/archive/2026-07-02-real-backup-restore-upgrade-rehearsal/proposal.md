## Why

DecisionAtlas already has backup/restore/upgrade documentation and a non-destructive evidence verifier, but the commercial roadmap still lacks proof that continuity can be rehearsed on real isolated runtime state. This change adds a safe real rehearsal lane so self-hosted customers can see backup, restore, upgrade validation, rollback planning, and evidence generation exercised without touching production data.

## What Changes

- Add a real backup/restore/upgrade rehearsal capability that runs only against an explicit scratch database/package workspace.
- Generate JSON and Markdown evidence for backup creation, restore validation, post-restore checks, package/version transition, post-upgrade checks, rollback plan, and custody boundaries.
- Preserve `pass`, `warning`, `operator_guided`, `not_provided`, `known_limitation`, and `blocking` states instead of converting missing continuity proof to pass.
- Update existing backup/restore/upgrade rehearsal language to distinguish non-destructive evidence verification from real scratch-environment rehearsal.
- Update self-hosted delivery, handoff, and Code Decision Audit reporting so real continuity evidence can be referenced when available.

## Capabilities

### New Capabilities

- `real-backup-restore-upgrade-rehearsal`: Defines real scratch-environment backup, restore, upgrade, rollback, and post-validation evidence generation.

### Modified Capabilities

- `backup-restore-upgrade-rehearsal`: Clarify the boundary between non-destructive verifier evidence and real scratch-environment continuity evidence.
- `self-hosted-delivery-rehearsal`: Require real continuity rehearsal evidence before claiming tested backup/restore/upgrade readiness.
- `team-handoff-reporting`: Include real continuity rehearsal status in customer/operator handoff reports when provided.
- `code-decision-audit-report-builder`: Reference real continuity rehearsal evidence in customer-readable audit reports when supplied.

## Impact

- New or updated CI/operator script for scratch continuity rehearsal.
- New template or fixture inputs for local/scratch continuity rehearsal.
- Updates to package/readiness/handoff/audit report generators.
- Tests for scratch database/package validation, missing inputs, unsafe paths, and downstream report integration.
- Documentation and update log entries explaining what is proven by real rehearsal versus operator-guided verifier evidence.
