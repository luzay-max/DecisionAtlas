## Context

The current self-hosted delivery evidence chain is broad but split across multiple commands:

- package build and verification
- clean install rehearsal
- external install evidence from explicit input
- release rehearsal bundle
- readiness history archive
- browser-level smoke tests

The project needs a customer-host rehearsal v2 layer that composes those signals into one delivery checkpoint. It must be honest about evidence boundaries because a solo developer's local machine, a clean local copy, and a customer-controlled host are three different proof levels.

## Goals / Non-Goals

**Goals:**

- Provide a single collector that emits customer-readable JSON/Markdown evidence for external/customer-host readiness.
- Accept explicit input paths and an optional sanitized host template.
- Preserve non-clean evidence states and explain rerun conditions.
- Support readiness-history archival for trend and release handoff.
- Keep the workflow runnable offline and safe for self-hosted evaluation.

**Non-Goals:**

- No billing, marketplace, multi-tenant SaaS, online license enforcement, or hosted operator platform.
- No automatic collection of secrets, raw `.env`, private repository content, customer logs, or database backups.
- No claim that a local clean install is a completed customer-host proof.
- No requirement to mutate live customer infrastructure from the collector.

## Decisions

### Decision: Compose existing evidence rather than duplicating checks

The v2 collector will read source evidence artifacts when present and classify each lane. This avoids duplicating package verification, clean install, release rehearsal, and external install logic.

Alternative considered: rerun every underlying check from the v2 collector. Rejected because it would be brittle, slow, and unsafe for customer-controlled environments.

### Decision: Use explicit template input for customer-host facts

The collector will support a sanitized JSON template that records host profile, operator, package identity, commands run, browser smoke result, and limitations.

Alternative considered: scrape logs or shell history automatically. Rejected because it risks collecting secrets or machine-specific private data.

### Decision: Archive output only when requested

The collector will write `.tmp` evidence by default and archive into readiness history only when explicitly requested.

Alternative considered: always archive. Rejected because scratch rehearsals and failed customer-host attempts should not automatically become durable release evidence.

## Risks / Trade-offs

- Customer-host input may still be incomplete -> classify missing lanes as `not_provided` or `operator_guided` and include next actions.
- Operators may paste sensitive material into the template -> reject obvious secret markers and document redaction expectations.
- Browser smoke may be run manually on a customer machine -> preserve manual evidence as bounded status rather than pretending an automated browser ran locally.
- Evidence could become too verbose -> output compact summaries and link source artifacts instead of copying full raw logs.
