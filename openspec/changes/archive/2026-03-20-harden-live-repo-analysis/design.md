## Context

DecisionAtlas has already solved two earlier trust problems: distinguishing demo data from imported data, and broadening imported evidence beyond issues, pull requests, and commits. The remaining gap is that live analysis still feels incidental rather than first-class. Users can run a demo import, but they cannot clearly start analysis for an arbitrary public repository, see which stage the system is in, or tell whether a poor outcome is caused by provider failure, import failure, or genuinely thin decision evidence.

The current architecture is already workspace-centric, with long-running GitHub imports represented as persisted jobs. That is a useful foundation, but the product currently over-compresses live analysis into a single job status and a fixed demo repository narrative. This change should strengthen the real-analysis path without broadening into GitHub App auth, private repository access, or full multi-workspace management.

## Goals / Non-Goals

**Goals:**
- Introduce a user-facing live-analysis entry for arbitrary public GitHub repositories.
- Preserve separation between the guided demo workspace and imported live-analysis workspaces.
- Expose staged job progress for import, indexing, extraction, and terminal states.
- Classify live-analysis failures and insufficient-evidence outcomes so the UI can explain them honestly.
- Establish a small benchmark set of public repositories that proves the live-analysis path works in practice.

**Non-Goals:**
- GitHub App installation, OAuth, or private repository access.
- Full workspace management UX such as workspace search, deletion, or sharing.
- Continuous sync, webhooks, or scheduled background refresh.
- Full source-code analysis beyond the current repository-document and GitHub artifact scope.

## Decisions

### 1. Introduce a dedicated live-analysis entry that creates or reuses imported workspaces per repository
The product should not overload the guided demo workspace with arbitrary repository imports. Instead, a user-submitted public repository should map to a distinct imported workspace keyed by a stable normalized repo identity. This keeps the existing workspace-centric navigation model intact while avoiding seed/live data mixing and avoiding the complexity of a general multi-workspace management product.

Alternative considered:
- Reuse the existing demo workspace and simply override the repo.
Why not:
- It would collapse demo and live semantics, pollute provenance, and make repeated live runs hard to reason about.

### 2. Extend import jobs with stage-aware status rather than fake percentage progress
The current system already persists import jobs, but a single `running` state is too coarse for real analysis. The model should expose explicit stages such as `queued`, `importing_artifacts`, `indexing_artifacts`, `extracting_decisions`, `succeeded`, and `failed`. This is more truthful and easier to implement than a percentage bar because the system does not currently have stable work-unit counts for every phase.

Alternative considered:
- Show a synthetic percentage progress bar.
Why not:
- It would look polished but would be misleading, especially when extraction time depends on provider latency and artifact signal.

### 3. Introduce explicit live-analysis outcome classification
The live path should distinguish between at least three broad outcomes:
- successful analysis with useful evidence
- successful analysis with insufficient evidence
- failed analysis due to operational/runtime error

Import job summaries and downstream read models should expose enough detail for the UI to explain whether a thin result is expected or whether the pipeline actually failed.

Alternative considered:
- Keep current generic failure and empty-state messaging.
Why not:
- That would continue to make real analysis feel unreliable even when the system is behaving correctly on a sparse repository.

### 4. Treat public benchmark repositories as part of the feature contract
Real-analysis capability should be proven on a small curated set of public repositories with different evidence shapes. This should not become a massive eval framework, but it should be enough to establish that the product works beyond `encode/httpx` and to guard against regressions in the live path.

Alternative considered:
- Rely on manual ad hoc repo testing.
Why not:
- It is hard to compare results over time and too easy to overfit to whichever repository happened to work last.

## Risks / Trade-offs

- [Workspace sprawl from user-submitted repos] → Reuse imported workspaces by normalized repo identity and defer full workspace-management UX.
- [Live analysis remains provider-sensitive] → Expose explicit failure categories and stage context rather than pretending the runtime is deterministic.
- [Thin repositories still disappoint users] → Distinguish insufficient evidence from failure in both job summaries and downstream page copy.
- [Benchmark repos drift over time] → Keep the benchmark set small and review expectations periodically rather than freezing brittle exact-output assertions.
- [Scope drifts into private repo/auth work] → Explicitly limit this change to public GitHub repositories and one-off analysis runs.

## Migration Plan

1. Add the live-analysis workspace creation/reuse path and route the new UI entry through existing workspace-centric pages.
2. Extend import job persistence and API serialization with stage and failure-classification fields.
3. Update web surfaces to show live-analysis stage state, terminal summaries, and insufficient-evidence messaging.
4. Add benchmark coverage for a curated public repo set and update docs to explain supported live-analysis scope.
5. Roll back by hiding the live-analysis entry and ignoring the new job metadata fields if the UX or runtime proves misleading.

## Open Questions

- Should imported workspaces created by live analysis be visible from a future workspace list immediately, or remain reachable only by redirect after submission in this phase?
- How many benchmark repositories are enough for this phase: three, five, or a small rotating set?
- Should the system reject very large repositories up front, or simply rely on existing page caps and surface longer-running jobs honestly?
