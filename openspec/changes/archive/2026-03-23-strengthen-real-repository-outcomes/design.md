## Context

DecisionAtlas has completed MVP construction and the main `v0.2` public-demo hardening slices. The guided demo lane is now intentionally stable, which shifts the main product risk to the real imported-workspace lane: imports may succeed while producing few candidate decisions, why-search may have little accepted-decision grounding, and drift is present as a concept but not yet operational enough for real repository usage.

The real-workspace problem has two sides:

1. Evidence supply is still thin for many repositories even after markdown ingest.
2. Product surfaces do not yet describe imported-workspace readiness strongly enough after a run completes.

This slice should improve both.

## Goals / Non-Goals

**Goals:**

- Increase the chance that a real public repository import yields reviewable candidate decisions.
- Make imported-workspace dashboard and downstream pages explain whether the workspace is ready for review, why-search, or drift.
- Tighten imported why-answer behavior so real answers are either citation-grounded in accepted decisions or explicitly blocked by missing evidence.
- Make imported drift evaluation easier to run and easier to interpret for imported workspaces.
- Add outcome-focused validation so future changes can be judged against real imported-workspace usefulness.

**Non-Goals:**

- Reworking the guided demo lane again
- Adding GitHub App auth, private repository support, login, or workspace permissions
- Replacing the drift system with a fully automatic continuous monitoring architecture
- Turning every weak repository into a rich-decision repository regardless of source quality

## Decisions

### 1. Introduce an imported-workspace readiness model

Imported workspaces should expose a small set of product-facing outcome states derived from existing signals such as candidate count, accepted count, latest import summary, and drift evaluation status.

This is preferred over exposing only raw counts because users need a next action, not just telemetry. The read model should answer questions like:

- is this workspace ready for review?
- is why-search trustworthy yet?
- has drift been evaluated since the latest import or acceptance?
- is this a sparse-evidence run rather than a failed run?

Alternative considered:

- Leave interpretation entirely to the UI from raw counts. Rejected because it repeats logic across pages and keeps the real lane hard to interpret.

### 2. Improve evidence supply before changing trust thresholds

The first lever should be better imported evidence selection and extraction prioritization, not simply weakening the confidence bar. Real outcomes improve more safely by importing and prioritizing rationale-heavy repository material such as architecture, migration, rollout, release, and operations markdown than by accepting weaker decision candidates.

Alternative considered:

- Lower extraction thresholds globally for imported workspaces. Rejected because it risks flooding review with lower-quality candidates and weakening trust.

### 3. Tighten imported why-answer gating around accepted decisions

Imported why-search should be treated as trustworthy only when it can ground the answer in accepted imported decisions and their source references. When imported workspaces do not yet have accepted-decision grounding, the system should return a structured, actionable explanation instead of a weak or over-optimistic answer.

Alternative considered:

- Let imported why-search answer directly from broader artifact evidence even when accepted decisions are absent. Rejected for now because it blurs the boundary between extracted memory and raw evidence search.

### 4. Keep drift evaluation explicit, but make it operational

Drift should remain operator-triggered for now, but the system should expose evaluation status, freshness, and guidance so imported workspaces do not feel inert. This keeps runtime cost and behavior legible while still making drift more useful in real analysis.

Alternative considered:

- Auto-run drift after every import or every acceptance. Deferred until outcome measurements show the extra cost is justified and the alert quality is good enough.

### 5. Validate against curated real repositories, not just the demo repo

This change should include benchmark-style validation against a small set of public repositories so progress is measured by imported-workspace usefulness, not just by unit tests or the seeded demo.

Alternative considered:

- Rely on ad hoc manual testing. Rejected because the exact problem is that real-lane quality is currently hard to evaluate consistently.

## Risks / Trade-offs

- [Richer document selection may import more noise] → Keep the selection conservative and outcome-driven; expand only rationale-heavy paths and report contribution summaries.
- [Imported why-search may feel stricter after gating] → Return clearer evidence-limited explanations and recommended next steps instead of weak answers.
- [Manual drift evaluation still adds a user step] → Expose explicit evaluation status and freshness so the step is understandable and not hidden.
- [Benchmark repos may still be uneven] → Use multiple curated public repositories and compare outcomes over time instead of expecting a single perfect benchmark.
- [More outcome states can complicate the UI] → Keep the readiness model compact and action-oriented.
