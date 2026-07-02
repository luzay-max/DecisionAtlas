## Context

DecisionAtlas can already build and verify a self-hosted package, rehearse clean install checks in an isolated local workspace, generate delivery readiness evidence, and produce handoff/audit reports. The remaining commercial proof gap is external installation evidence: a clean VM, another machine, or customer-controlled host should be able to produce a bounded evidence bundle that can be reviewed without exposing secrets.

The design should avoid pretending that this agent can directly control a customer machine. Instead, the product should provide a local verifier that accepts operator-submitted evidence generated on the external host, classifies each lane, redacts sensitive material, and integrates the result into delivery artifacts.

## Goals / Non-Goals

**Goals:**

- Define a deterministic external install evidence input and output format.
- Validate external host evidence without requiring raw logs, `.env`, tokens, private source files, or database dumps.
- Preserve non-pass states such as `operator_guided`, `not_provided`, `warning`, and `blocked`.
- Let delivery rehearsal, handoff reports, and Code Decision Audit reports reference external install evidence.
- Keep evidence useful for self-hosted paid pilots and customer acceptance.

**Non-Goals:**

- Provision remote VMs, cloud infrastructure, or customer machines automatically.
- Run destructive backup/restore/upgrade operations.
- Collect raw private repository content, raw model output, or screenshots containing private code.
- Add SaaS billing, hosted multi-tenancy, self-service OAuth, Marketplace flows, or online license enforcement.
- Replace existing clean install or package verification flows.

## Decisions

1. Use operator-submitted evidence rather than remote orchestration.

   Rationale: self-hosted customers control their own environment. A verifier that consumes sanitized evidence is safer and more realistic than trying to automate remote host control.

   Alternative considered: SSH/WinRM-based remote runner. Rejected because credentials, network topology, and customer security policies would create more risk than value for this stage.

2. Produce both JSON and Markdown.

   Rationale: JSON can feed release/handoff/audit automation; Markdown can be reviewed by operators and customers without a running backend.

   Alternative considered: Markdown-only checklist. Rejected because downstream evidence history and report builders need structured status.

3. Treat missing external proof as explicit, not failed by default.

   Rationale: local development should remain usable, but customer-facing material must not overstate readiness. Missing external proof should become `not_provided` or `operator_guided` and should carry next actions.

   Alternative considered: fail every delivery rehearsal without external proof. Rejected because many local or Community evaluations do not require customer-host claims.

4. Require redaction checks.

   Rationale: external install evidence is likely to originate from private environments. The verifier should reject obvious token-like strings, `.env` secret assignments, private key markers, raw backup content markers, and unbounded private paths.

   Alternative considered: rely on operator discipline only. Rejected because evidence artifacts may be committed or sent to customers.

5. Integrate by reference.

   Rationale: delivery rehearsal, handoff, and audit reports should summarize external evidence status and paths rather than copying raw external evidence wholesale.

   Alternative considered: embed every external evidence field into all downstream reports. Rejected because it increases leakage risk and makes report schemas brittle.

## Risks / Trade-offs

- [Risk] Operator-submitted evidence can be falsified or incomplete -> Mitigation: record host profile, package identity, command checklist, evidence timestamp, and limitations; do not claim cryptographic attestation.
- [Risk] Sanitization may miss sensitive values -> Mitigation: reject common secret markers and document that operators must review Markdown before sharing.
- [Risk] External proof can become a blocker for all local work -> Mitigation: only require it when customer/external host readiness is claimed.
- [Risk] Public repo import checks may be flaky due to network/provider state -> Mitigation: allow explicit `operator_guided`, `not_provided`, or `warning` states with rerun conditions.

## Migration Plan

1. Add a template external evidence input file.
2. Add a verifier/collector that emits JSON and Markdown.
3. Add tests for status classification, redaction, and required lanes.
4. Update delivery, handoff, and audit report generators to accept optional external install evidence.
5. Update docs and package verification expectations so operators know this is separate from local clean install rehearsal.

Rollback is low risk: remove the new verifier and optional downstream input fields. Existing package verification, clean install, delivery rehearsal, and report generation remain compatible.

## Open Questions

- Should external host evidence eventually support signed attestations, or is operator-submitted evidence enough for early pilots?
- Which public repository should be the default external smoke target: `fastapi`, `encode/httpx`, or an operator-provided repository?
- Should screenshots be allowed only as private/local artifacts, or should the verifier support explicit screenshot metadata without storing images?
