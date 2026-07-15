## Context

The repository already has a package builder, offline verifier, clean-install rehearsal, customer-host v2 template, real external-host evidence collector, readiness-history archive, and team browser rehearsal. The gap is operational: an operator still has to invent the trial input shape and manually decide which observations prove the product's actual delivery loop. The collector also needs to guarantee that evidence shared from a host cannot expose absolute external paths.

The change is intentionally evidence-first. It does not turn the collector into a deployment agent, and it does not claim that a local Docker run is a customer-controlled host. An actual external host or independently controlled VM must supply the facts; an isolated local rehearsal can validate the kit and remain `operator_guided`.

## Goals / Non-Goals

**Goals:**

- Define one versioned, sanitized host-trial input contract for package identity, startup, health, admin access, team/workspace setup, repository import, review, Why, Drift, backup/recovery, and browser smoke.
- Make the collector aggregate those lanes into a bounded proof level and preserve warnings, blockers, operator guidance, and missing evidence.
- Redact absolute paths from JSON, Markdown, warnings, and readiness-history references.
- Provide an operator checklist and commands that can be executed on a clean host and attached to a handoff.
- Exercise the kit against an isolated host simulation and, when available, a real non-development host without inventing pass evidence.

**Non-Goals:**

- Automatically installing software, starting Docker, importing repositories, changing customer infrastructure, or uploading evidence.
- Adding hosted SaaS, billing, multi-tenancy, self-service OAuth, runtime license enforcement, or enterprise SSO.
- Treating local development-stack or local Docker results as external customer proof.
- Recording credentials, raw logs, private repository content, raw backups, or raw model output.

## Decisions

1. **Use a versioned operator input rather than runtime orchestration.** The host operator already controls credentials and infrastructure. A JSON contract is reviewable, can be filled outside the repository, and keeps the collector deterministic and non-destructive. A deployment orchestrator was rejected because it would require privileged credentials and make evidence collection mutate customer systems.

2. **Represent the trial as named lanes.** Each core action has a bounded status and short summary: package, startup, health, admin login, team/workspace, repository import, review, Why, Drift, continuity, browser smoke, and redaction. This makes a partial trial explainable and allows a missing customer capability to remain `operator_guided` instead of collapsing the whole report into an ambiguous warning.

3. **Derive proof level from host control and lane state.** A fully populated template is not sufficient. `real_external_customer_controlled` requires customer-controlled host acknowledgement, non-template values, passed browser smoke, and no non-pass core lanes. Local or example inputs remain template/operator-guided even if every supplied lane says `passed`.

4. **Use repository-relative or redacted paths.** Evidence may refer to files inside the repository by relative path. Paths outside the repository are represented as `<external-path>`; absolute drive paths never reach archived JSON or Markdown. This is safer than trying to infer whether an external path is sensitive.

5. **Archive through the existing readiness-history builder.** The trial report remains a source family in the existing index/trend model so release and handoff summaries can consume it without creating a second history format.

## Risks / Trade-offs

- [Risk] Operators may fill plausible values without actually running the flow. -> Require explicit host-control acknowledgement, command summaries, browser status, and operator identity; document that the collector validates claims but cannot independently attest to them.
- [Risk] A real customer host may not expose a public URL or model provider. -> Keep URL/provider fields optional and classify the affected lane `operator_guided` or `not_provided`; do not block private/local deployments unless a required lane is explicitly failed.
- [Risk] Existing templates and historical evidence use absolute paths. -> Sanitize new output at the collector boundary and add regression assertions; do not rewrite unrelated historical records automatically.
- [Risk] Core-lane expansion can make small trials appear incomplete. -> Keep the lane vocabulary bounded, allow explicit `not_applicable` with a reason for unsupported claims, and expose the follow-up action in Markdown.
- [Risk] External host evidence may contain secrets in free-text summaries. -> Scan the entire input and source payloads for known secret markers, return `blocking`, and never render the matching raw value.

## Migration Plan

1. Add the new schema/template and collector lane validation with backward-compatible handling for existing customer-host v2 inputs.
2. Add tests for legacy input, complete sanitized input, missing lanes, template markers, secret markers, external paths, and readiness-history archival.
3. Run an isolated package/stack rehearsal where available and record it as `operator_guided` unless the host is independently customer-controlled.
4. For an actual customer/VM trial, fill the input on that host, run the documented commands, collect JSON/Markdown, and archive the dated evidence entry.
5. Rollback is documentation-only: older input files remain accepted, and removing the new optional lanes restores the previous collector behavior.

## Open Questions

- Which independent VM or customer-controlled host will provide the first clean external proof?
- Should a future release require a real external host trial for every package version, or only for major deployment/runtime changes?
