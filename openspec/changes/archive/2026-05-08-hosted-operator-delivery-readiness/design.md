## Context

Hosted preview support already exists across several documents and scripts: hosted health checks, hosted smoke checks, seeded demo reset/reseed, seeded readiness checks, governance guardrail summaries, optional live real-repo benchmark evidence, and release evidence bundles. The remaining gap is operational cohesion: an operator still has to assemble stop/go readiness, recovery status, and limitation disclosures manually before an external preview.

This design adds a thin hosted/operator delivery readiness layer that aggregates existing signals into a bounded readiness artifact and makes the runbook flow explicit.

## Goals / Non-Goals

**Goals:**
- Provide a local command that writes hosted/operator readiness JSON and Markdown from explicit inputs.
- Preserve pass/blocking/non-blocking/known-limitation/operator-guided classification per lane.
- Record hosted URL availability, seeded demo readiness, health/smoke evidence, recovery drill status, governance guardrail status, optional release evidence, and optional real-repo benchmark evidence.
- Make public walkthrough stop/go rules explicit.
- Keep default reset/reseed scoped to `demo-workspace` and preserve imported workspace boundaries.
- Keep hosted/operator checks separate from the canonical release gate.

**Non-Goals:**
- No hosted SaaS control plane, dashboard, billing, tenant administration, Marketplace, self-service OAuth, or secret vault work.
- No automatic deployment or external infrastructure provisioning.
- No default network-heavy validation unless an operator supplies hosted URLs and explicitly runs checks.
- No destructive cleanup of imported workspaces or governance history.
- No conversion of advisory guardrail output into default CI enforcement.

## Decisions

### Readiness Artifact Instead Of Hosted Dashboard
Implementation should create a local readiness artifact, not a new UI. JSON supports automation and Markdown supports operator handoff. This fits the current maturity stage and avoids introducing hosted state management before the operator flow stabilizes.

### Explicit Inputs And Operator-Guided Missing State
The command should accept explicit statuses, hosted URLs, and optional source report paths. If hosted URLs or optional reports are absent, the output should classify those lanes as `operator_guided`, `known_limitation`, or `not_provided` rather than pretending the hosted environment passed.

### Lane-Based Classification
The artifact should model lanes rather than one opaque score:
- core hosted services
- seeded public walkthrough
- recovery drill
- governance second act
- release evidence
- optional real-repo credibility evidence

Core service and seeded walkthrough blockers should stop an external public walkthrough. Optional lanes can be excluded or marked non-blocking if the public walkthrough remains stable.

### Reuse Existing Checks
The new layer should not duplicate health, smoke, seeded readiness, release evidence, or benchmark logic. It should consume their outputs or explicit operator status and link to the commands to rerun them.

### Non-Mutating By Default
Readiness generation should not reset, reseed, import repositories, run live benchmarks, create tags, push commits, or publish releases. It records evidence; operators run recovery/check commands separately.

## Risks / Trade-offs

- **Risk: false confidence from missing hosted URLs.** Mitigation: missing hosted URL evidence is classified as operator-guided or known limitation, not pass.
- **Risk: optional lanes block demos unnecessarily.** Mitigation: separate stable public walkthrough from optional governance/imported/benchmark lanes.
- **Risk: stale report paths.** Mitigation: record source path and generated timestamp for every consumed artifact.
- **Risk: destructive recovery misunderstanding.** Mitigation: docs and readiness output state that default reset/reseed scopes to `demo-workspace`.
- **Trade-off: no hosted dashboard yet.** A file-based artifact is less polished but faster, safer, and easier to version before investing in hosted operator UI.
