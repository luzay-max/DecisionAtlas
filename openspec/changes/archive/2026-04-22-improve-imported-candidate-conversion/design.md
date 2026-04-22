## Context

DecisionAtlas already distinguishes imported runs that are `review_ready`, `evidence_limited`, or `conversion_limited`, and it already records extraction counters and conversion-loss reasons for screened-in artifacts. The remaining real-lane gap is narrower: some imported runs now identify enough high-signal artifacts to justify full extraction, but the current conversion path still leaves those artifacts without grounded candidate decisions often enough that the workspace never reaches a trustworthy first review step.

The existing pipeline has strong guardrails that should stay intact:

- candidate decisions still need grounded evidence
- imported why should stay anchored on accepted decisions rather than raw artifact search
- broad ingest expansion is out of scope for this slice

This change therefore targets the screened-in-to-candidate segment of the imported extraction funnel rather than the broader import, why, or drift systems.

## Goals / Non-Goals

**Goals:**

- Improve candidate creation for screened-in imported artifacts that already show strong decision signal.
- Reduce repeated `conversion_limited` outcomes on selected benchmark repositories without weakening candidate trust boundaries.
- Preserve current readiness semantics while allowing more imported workspaces to advance into `review_ready`.
- Protect the improvement with lightweight benchmark expectations tied to curated public repositories.

**Non-Goals:**

- Expanding platform scope into GitHub App auth, private repositories, login, or owner-scope UX
- Broadening ingest to many new document families
- Replacing imported why gating or drift semantics
- Lowering grounding requirements just to increase candidate counts

## Decisions

### 1. Introduce a bounded conversion-recovery path after first-pass extraction

The pipeline should keep its current shortlist and screening behavior, but when a screened-in artifact fails first-pass conversion for recoverable reasons, it should run one bounded recovery extraction attempt before the artifact is classified as conversion loss.

The recovery path should be reserved for artifacts that still look strong enough to justify another pass, such as:

- rationale-heavy docs whose first extraction payload was too diffuse
- PRs whose decision signal is present but not surfaced clearly enough in the first prompt family
- artifacts that produce partial decision structure but fail quote grounding or other recoverable conversion checks

This is preferred over simply relaxing candidate thresholds because the problem is not only confidence; it is often that the first extraction pass was not packaged well enough for the artifact family.

Alternative considered:

- Lower candidate creation thresholds globally. Rejected because it would improve counts by weakening trust instead of improving conversion quality.

### 2. Refine artifact-family routing inside the screened-in extraction path

The current extraction families are useful but still coarse for imported docs. The design should refine family selection within the existing screened-in path using artifact metadata that already exists or can be derived conservatively, such as document signal category, path cues, title cues, and artifact type.

The goal is not to create many prompt families. The goal is to avoid sending materially different rationale-bearing artifacts through one overly generic path when they would convert better with a more targeted extraction shape.

Alternative considered:

- Keep existing families and only tune prompt text. Rejected because the current bottleneck is likely as much about artifact packaging and routing as raw prompt wording.

### 3. Package extraction input around conversion-oriented evidence windows

For recovery-eligible artifacts, the system should prepare a second extraction payload that is more explicitly centered on grounded decision evidence:

- preserve the strongest rationale-bearing sections
- bias toward quote-rich local context that can later be grounded
- keep the payload bounded so the recovery path does not become an unbounded retry loop

This is preferred over importing broader context because the main issue is likely evidence packaging, not lack of total repository content.

Alternative considered:

- Expand import coverage again. Rejected because previous slices already improved evidence supply, and this change is meant to improve conversion of already-screened-in evidence.

### 4. Preserve readiness semantics, but make `conversion_limited` a later outcome

The product-facing readiness model should continue to distinguish `review_ready`, `evidence_limited`, and `conversion_limited`, but `conversion_limited` should remain the outcome only after the refined conversion path has been attempted and still yields no reviewable candidates.

This keeps the user-facing states stable while making the conversion pipeline more ambitious before it declares that extraction quality was the limiting factor.

Alternative considered:

- Add a new readiness state for “conversion retry in progress” or similar. Rejected because this slice should improve the existing funnel, not add more state complexity to the product.

### 5. Protect the slice with conversion-focused benchmark expectations

The benchmark layer should keep the current why and drift protections, but it should also add repo-level expectations for candidate conversion so the project can tell whether this slice actually moved a real imported repository from a stalled conversion funnel toward reviewable output.

Alternative considered:

- Rely on ad hoc manual re-runs. Rejected because the exact problem is repeatability on real repos.

## Risks / Trade-offs

- [Recovery attempts increase extraction cost] → Keep the recovery path bounded to one additional pass for selected recoverable failures only.
- [Finer family routing may overfit to current benchmark repos] → Base routing on conservative artifact metadata already used elsewhere and protect broad behavior with fixtures across multiple repos.
- [Improved conversion may tempt weaker grounding] → Keep grounding checks unchanged and treat ungrounded outputs as failed conversion, not as acceptable candidates.
- [Benchmarks may still lag behind real-world repo variety] → Use benchmarks to protect representative regressions, not to claim universal repository coverage.

## Migration Plan

No external migration should be required. This change is an internal pipeline and benchmark refinement.

Deployment should follow the existing release-validation path:

1. run unit and integration tests for extraction, import jobs, and imported readiness
2. run benchmark fixture validation
3. run bounded live real-repo validation against the curated repositories

Rollback is straightforward: revert the refined conversion routing and recovery path while preserving the existing readiness model.

## Open Questions

- Which recovery failure classes should be considered eligible for a second pass: only structural parse failures, or also thin grounding cases?
- How many refined document families are enough before the routing logic becomes harder to trust than the current coarse families?
- Should benchmark success for this slice require a minimum absolute candidate count on one target repo, or only an improvement relative to prior `screened_in_artifacts` behavior?
