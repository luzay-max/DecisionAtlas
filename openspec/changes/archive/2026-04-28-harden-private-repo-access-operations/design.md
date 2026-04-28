## Context

DecisionAtlas v0.3 now has admin-facing token-backed private repository access binding. The current path is usable, but the operational contract is still shallow: users can see a source label and status, yet failures can still feel generic, authorization details are not guaranteed across every product surface, and operator guidance does not fully explain token permissions, rotation, or troubleshooting boundaries.

This change hardens the existing token-backed access-source lane without introducing a secret vault, GitHub OAuth, Marketplace setup, or full organization administration. The implementation should reuse current access-source records, owner-scope session authority, and existing import/lookup surfaces.

## Goals / Non-Goals

**Goals:**

- Make private repository failures actionable by separating missing source, unauthorized/revoked source, repository not found, provider/network failure, and validation errors.
- Show token-backed access-source label, authorization status, and bounded detail consistently on lookup, live-analysis, dashboard, and readiness surfaces.
- Preserve credential safety: tokens are write-only product inputs and never appear in responses, reusable summaries, logs, or tests.
- Keep private access setup admin-only and current-scope-derived.
- Document operator expectations for token permissions, rotation, troubleshooting, and known non-goals.

**Non-Goals:**

- No secret vault or encrypted credential-management UI.
- No token rotation history or audit log UI.
- No GitHub OAuth / Marketplace private repo onboarding.
- No organization member-management expansion.
- No provider-dependent live private repository check in default CI.

## Decisions

1. Keep access-source records as the authority for private repository credentials.

   The current model already separates workspace identity from credential-bearing owner-scoped access sources. Reusing it avoids schema churn and keeps the hardening focused on semantics, status propagation, and tests. Alternative considered: add a new credential vault abstraction now. Rejected because it would expand scope beyond v0.3 hosted-preview readiness.

2. Normalize failure outcomes at the engine boundary before product rendering.

   Engine lookup/import/bind paths should return bounded categories that the API and web can display without inspecting provider exception strings. This keeps UI copy stable and prevents raw provider details or token-related data from leaking. Alternative considered: map failures only in the web app. Rejected because API and future clients would still receive ambiguous outcomes.

3. Treat authorization detail as bounded operational text, not raw provider payload.

   Product surfaces may display details such as "token revoked or lacks repository access", but MUST NOT echo token values or full provider response bodies. This gives users enough recovery context while preserving credential safety.

4. Preserve current role and scope behavior.

   Private access binding remains admin-only and current owner scope remains session-derived. The UI must not add typed owner-scope overrides, and tests should cover non-admin denial and token non-echo behavior.

5. Keep live private-repo verification optional in release workflows.

   Default CI should use deterministic mocked provider tests. Operator docs can describe manual live validation with real private credentials, but hosted-preview readiness should not require exposing real tokens to CI.

## Risks / Trade-offs

- [Risk] Failure categories may hide provider-specific nuance. → Mitigation: keep categories stable and include bounded detail where safe.
- [Risk] Token status can become stale after GitHub permission changes. → Mitigation: update access-source authorization status on bind/import failures and document manual rotation/rebind expectations.
- [Risk] UI surfaces drift in wording. → Mitigation: centralize or reuse existing access-source label/status helpers where practical and cover key surfaces with tests.
- [Risk] Operators may mistake this for production-grade secret management. → Mitigation: explicitly document non-goals and token handling boundaries.

## Migration Plan

- No database migration is expected unless implementation discovers missing status fields.
- Existing token-backed workspaces continue to use their current access-source references.
- New failure/status semantics should be backward compatible with existing access-source records.
- Rollback is limited to reverting product copy/status classification changes; stored workspace/access-source data remains compatible.

## Open Questions

- Whether to add a small shared web helper for access-source status labels if duplication is found during implementation.
- Whether authorization detail should be persisted on every failed import attempt or only updated during binding/import validation failures.
