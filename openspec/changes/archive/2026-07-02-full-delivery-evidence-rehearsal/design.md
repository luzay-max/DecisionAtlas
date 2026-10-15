## Context

Readiness history currently archives release evidence, hosted readiness, and benchmark comparison. That was enough before the project added external install evidence, real continuity evidence, handoff reports, and Code Decision Audit reports. The product direction now requires a customer/operator to see one dated evidence history entry that includes the whole delivery packet.

## Goals / Non-Goals

**Goals:**

- Add explicit evidence families for external install, real continuity rehearsal, team handoff, and Code Decision Audit.
- Copy supplied JSON/Markdown artifacts into a dated readiness history entry.
- Summarize each family without copying secrets, raw backups, private repository content, or raw local logs.
- Keep missing evidence visible as `not_provided`.
- Keep trend/index output readable without requiring a running backend.

**Non-Goals:**

- Generate the underlying evidence artifacts; existing scripts remain responsible for that.
- Scan `.tmp` implicitly or infer files from local state.
- Upload evidence to external services.
- Add SaaS billing, hosted multi-tenancy, Marketplace/OAuth, or license enforcement.

## Decisions

1. Extend the existing readiness history archiver rather than creating a parallel full-delivery archiver.

   Rationale: readiness history already owns dated durable evidence entries and trend/index output. Adding families there keeps the evidence model coherent.

2. Use family-specific summarizers.

   Rationale: external install, real continuity, handoff, and audit reports expose different status fields. Compact summaries make index/trend useful while avoiding raw evidence copying.

3. Preserve explicit input only.

   Rationale: release evidence must be repeatable and honest. The archiver should not scan `.tmp` and should not synthesize pass evidence from local state.

## Risks / Trade-offs

- [Risk] History entries become too wide -> Mitigation: index shows compact family statuses and key counts; full JSON remains in each entry.
- [Risk] Sensitive data leaks through summaries -> Mitigation: summarize only status/count/bounded fields and reuse explicit copy behavior without embedding raw source content in index.
- [Risk] Older history entries lack new families -> Mitigation: missing families appear as `not_provided` only for new archive commands that omit them; old entries remain readable.

## Migration Plan

1. Add new family constants, labels, summarizers, CLI args, index columns, and trend fields.
2. Update tests for archive, omitted sources, artifact copying, and trend output.
3. Update docs and update log.
4. Run relevant Python tests and OpenSpec strict validation.
