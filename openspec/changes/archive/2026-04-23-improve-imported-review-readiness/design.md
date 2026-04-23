## Context

The current imported-lane baseline is stronger than it was before: real repositories more often reach `review_ready`, the product distinguishes running/evidence-limited/conversion-limited states, and imported why answers fail closed when accepted grounding is missing. The remaining gap is that review-ready workspaces still flatten two materially different states into one surface: "candidates exist" and "an accepted baseline now exists". In practice, the first accepted decision is the point where imported workspaces start becoming meaningfully reusable for why, drift, and downstream trust.

This change crosses engine readiness modeling, web imported-lane UX, and benchmark fixtures. It needs a design because the same milestone must drive dashboard/search guidance, why support expectations, and regression protection without introducing a new state explosion.

## Goals / Non-Goals

**Goals:**
- Treat the first accepted imported decision as a first-class product milestone.
- Refine imported readiness summaries and recommended actions so users are pushed toward the highest-value next step.
- Improve imported why readiness after that first accepted baseline without weakening why trust boundaries.
- Capture the new review-readiness and first-accepted-baseline expectations in lightweight benchmark fixtures.

**Non-Goals:**
- Redesign the entire candidate review workflow or add new moderation tooling.
- Change platform scope, auth, private repo access, or GitHub App behavior.
- Weaken why answer support grading or bypass accepted-decision grounding.
- Introduce a large benchmark platform or live-only validation dependency.

## Decisions

### 1. Keep the readiness model compact, but add an accepted-baseline milestone
We will not invent a broad new readiness taxonomy. Instead, we will refine the existing imported readiness contract so `review_ready` can distinguish between "review is available" and "accepted baseline established" through the primary next action, recommended actions, and explicit why/drift downstream state. This keeps the product contract stable while making the first accepted decision visible.

Alternative considered:
- Add an entirely new top-level readiness state between `review_ready` and `why_ready`.
Why not:
- It would add product complexity across dashboard, search, and tests for limited gain. The stronger distinction belongs in action routing and downstream readiness, not another headline state.

### 2. Optimize for the first high-value acceptance, not generic review throughput
The product should steer imported workspaces toward accepting the first strong decision instead of treating all candidate review as equivalent busywork. The design assumes the first accepted decision unlocks a bounded but real improvement in imported why readiness, even if the workspace has not yet accumulated a broad accepted corpus.

Alternative considered:
- Continue treating accepted decisions only as a bulk threshold for why-readiness.
Why not:
- It hides the first useful product outcome and makes imported review feel inert until too late.

### 3. Preserve why trust semantics while allowing first-accepted uplift
Imported why should become more usable after the first accepted decision only when the question can be grounded to that accepted decision with citations. We will not upgrade weak answers just because the workspace now contains one accepted decision. The design therefore tightens the relationship between accepted-baseline progress and support grading instead of loosening support thresholds.

Alternative considered:
- Mark imported why broadly available after any accepted decision exists.
Why not:
- That would blur the current trust boundary and regress the fail-closed behavior that was intentionally added.

### 4. Protect the change with fixture-backed repository milestones
Curated benchmark fixtures will express review-readiness milestones such as minimum accepted decisions or expected why readiness after a first acceptance on selected repositories. This keeps the regression surface lightweight and reproducible.

Alternative considered:
- Rely only on narrative smoke notes or live stack reruns.
Why not:
- The behavior is too product-critical to leave unprotected, and live-only checks are too expensive for the default loop.

## Risks / Trade-offs

- [Risk] The product may overstate why readiness after a single acceptance.  
  Mitigation: keep why support grading anchored to accepted decision grounding and citations, not to acceptance count alone.

- [Risk] More nuanced imported readiness could confuse UI copy or create inconsistent surfaces.  
  Mitigation: keep the state model compact and drive all surfaces from backend-provided next actions and downstream readiness fields.

- [Risk] Benchmark expectations become brittle if they depend on exact accepted counts across noisy repositories.  
  Mitigation: use bounded milestone-style expectations on curated repos rather than exact full-output snapshots.

- [Risk] Review UX may still underperform even if readiness semantics improve.  
  Mitigation: separate semantics/routing changes from broader workflow redesign and keep the change focused on first useful outcome signaling.

## Migration Plan

1. Update imported readiness/outcome modeling in the engine to surface first-accepted-baseline progress and refined next actions.
2. Update dashboard/search/review-facing imported UX to consume the refined contract rather than local heuristics.
3. Update why support/readiness logic so a first accepted baseline improves imported why availability only when grounded support is present.
4. Add or extend lightweight benchmark fixtures to protect these milestones on curated repositories.
5. Validate with fixture-backed checks and selected live smoke repositories before archive.

Rollback is straightforward: revert the readiness/why contract changes and restore the previous imported-lane summaries and fixture expectations.

## Open Questions

- Which curated repositories should become the canonical "first accepted baseline" protection cases beyond the existing why/drift regressions?
- Should the product expose accepted-baseline progress numerically in imported readiness, or keep it qualitative through next actions and readiness states only?
