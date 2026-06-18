## Context

DecisionAtlas self-hosted documentation already explains backup, restore, upgrade, rollback, clean install, package verification, release evidence, readiness history, and handoff evidence. The missing layer is a bounded rehearsal artifact that can be run safely before customer handoff and can preserve operator-guided states when real backup/restore evidence is not yet available.

The rehearsal must support self-hosted sales and pilot claims without becoming a destructive database utility. Customer backups and credentials remain operator-controlled and must not be copied into committed files.

## Goals / Non-Goals

**Goals:**

- Provide JSON and Markdown backup/restore/upgrade rehearsal evidence.
- Validate that backup, restore, upgrade, rollback, credential custody, and post-upgrade verification lanes are explicitly represented.
- Preserve `pass`, `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states without converting missing evidence into pass.
- Detect obvious secret/token/private-key leakage in rehearsal inputs and Markdown outputs.
- Integrate the rehearsal with self-hosted delivery, commercial baseline, package verification expectations, tests, and update logs.

**Non-Goals:**

- Do not run `pg_dump`, restore PostgreSQL, mutate Redis, run migrations, or perform rollback automatically.
- Do not implement online license enforcement, SaaS billing, hosted secret vault, enterprise SSO, or managed operations.
- Do not commit customer backups, private repository content, `.env`, provider keys, or token material.

## Decisions

1. Use a non-destructive evidence verifier instead of a destructive restore tool.

   Rationale: A customer-ready continuity claim needs proof of operator steps and evidence references, but CI and local development should not restore production databases. The verifier checks shape, status, custody, and evidence links while leaving destructive operations to the operator.

   Alternative considered: adding scripts that run `pg_dump` and restore into a temporary database. This would be useful later, but it introduces environment-specific PostgreSQL tooling and higher risk before the evidence contract is stable.

2. Treat missing real evidence as `operator_guided` or `not_provided`, not failure by default.

   Rationale: Early self-hosted pilots often cannot perform a full restore/upgrade rehearsal on every run. The value is preserving truthful state so customer-facing claims do not overstate readiness.

   Alternative considered: require all lanes to pass. That would make local CI too brittle and encourage fake evidence.

3. Require all continuity lanes in the input schema.

   Rationale: The rehearsal should force operators to consciously address backup, restore, upgrade, rollback, custody, and post-upgrade verification instead of only documenting the happy path.

4. Keep generated reports in `.tmp` unless archived into readiness history.

   Rationale: Rehearsal evidence may include local paths, operator notes, and environment-specific status. Durable customer claims should copy only reviewed artifacts into readiness history.

## Risks / Trade-offs

- Non-destructive checks may be mistaken for actual restore proof -> reports and docs must state whether a real restore was executed.
- Operators may omit backup artifact details and still get a non-blocking report -> missing real evidence remains visible as `operator_guided` or `not_provided`.
- Secret detection is pattern-based and not exhaustive -> human review remains required before sharing.
- A future real restore runner may need environment-specific PostgreSQL support -> keep the current verifier schema stable so it can wrap real restore evidence later.
