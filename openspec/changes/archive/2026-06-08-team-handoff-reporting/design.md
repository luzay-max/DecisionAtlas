## Context

DecisionAtlas now supports team accounts, workspace permissions, multiple Git sources, collaborative audit history, readiness evidence history, and offline self-hosted packaging. The missing product layer is a repeatable handoff report that an admin can give to a team lead, customer, or operator to explain the current workspace state and delivery evidence without manually stitching together JSON files, screenshots, and logs.

The report must work in self-hosted/offline environments. It should consume existing local state and evidence files, generate deterministic JSON and Markdown, and avoid exposing secrets, raw repository tokens, or unnecessary private source content.

## Goals / Non-Goals

**Goals:**

- Generate a team/customer-readable handoff report in JSON and Markdown.
- Summarize workspace, repository sources, decisions, review history, drift posture, governance status, readiness evidence, and benchmark comparison.
- Preserve non-clean states such as warning, blocking, not-provided, operator-guided, and known-limitation.
- Support self-hosted release rehearsal and customer handoff without requiring network access.
- Add deterministic tests and a browser/operator rehearsal that opens the generated Markdown as a human would.

**Non-Goals:**

- Do not build a full BI/report designer.
- Do not export raw private repository content.
- Do not expose tokens, local secret paths, or raw model prompts.
- Do not replace readiness evidence history, benchmark comparison, or audit trail storage.
- Do not introduce SaaS billing, multi-tenant reporting, marketplace OAuth, or license enforcement.

## Decisions

1. Generate reports from local files and existing API-shaped summaries first.

   Rationale: self-hosted customers need offline evidence. A file-first generator can reuse existing `.tmp` outputs, readiness history, and backend exports without adding a new runtime dependency.

   Alternative considered: create a new always-on reporting service. Rejected for this stage because it adds deployment and security complexity before the report schema is stable.

2. Emit both JSON and Markdown.

   Rationale: JSON supports automated release evidence, while Markdown supports customer/operator handoff and browser rehearsal.

   Alternative considered: Markdown only. Rejected because future trend and release gates need machine-readable evidence.

3. Keep report sections explicitly bounded.

   Rationale: a handoff report should answer "what is ready, what changed, what remains risky" without becoming a data dump. Each section should include counts, representative items, source evidence references, and limitations.

   Alternative considered: include full raw audit or benchmark payloads. Rejected because it is noisy and increases secret/private-data risk.

4. Treat unavailable evidence as first-class status.

   Rationale: a self-hosted/offline report must not silently claim success when live repository tests, private token validation, or hosted readiness were not provided.

   Alternative considered: omit missing sections. Rejected because omission makes the report look cleaner than the actual delivery state.

## Risks / Trade-offs

- Report completeness depends on available source evidence -> The generator will mark missing or stale inputs explicitly instead of inferring pass.
- Reports could accidentally expose sensitive material -> The generator will use bounded fields and tests will verify known secret-like files and token fields are not included.
- File-first reporting can drift from runtime UI semantics -> Tests will pin the report schema and docs will describe report inputs as release evidence snapshots, not live dashboards.
- Markdown can become too long for customer handoff -> The first version will include compact counts plus selected examples, with JSON retaining full structured evidence where appropriate.
