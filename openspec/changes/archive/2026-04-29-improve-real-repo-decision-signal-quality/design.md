## Context

The v0.3 RC already exposes imported candidate quality data through the decisions API and renders quality cues in the review queue. The remaining problem is not missing infrastructure; it is calibration and reviewer usefulness. A candidate with high confidence but weak source refs or missing provenance must not be presented as a strong baseline candidate, and quality reports should make thin-candidate pressure easy to inspect.

This slice intentionally avoids changing the extraction prompt or the LLM pipeline. It improves the signal model around already extracted candidates so future extraction and why-search work has a better baseline.

## Goals / Non-Goals

**Goals:**

- Tighten the `strong`, `partial`, and `thin` candidate quality boundaries.
- Make review-card quality reasons readable and actionable.
- Ensure high confidence alone cannot promote a candidate to `strong`.
- Improve benchmark/report output around label distribution, thin pressure, provenance gaps, and first-baseline usefulness.
- Add boundary tests for quality labels and review rendering.

**Non-Goals:**

- No rewrite of the extraction pipeline or decision-extraction prompt.
- No database migration unless an implementation detail proves it is already unavoidable.
- No free-form LLM scoring of candidate quality.
- No new review workflow, approval state, or collaboration model.

## Decisions

### Decision 1: Keep candidate quality deterministic

Candidate quality should continue to derive from observable facts: source-ref count, previewable quote count, artifact provenance, source URL availability, and confidence bucket. This keeps quality labels testable and avoids introducing another model-dependent judgment layer.

Alternative considered: ask an LLM to grade candidate usefulness. That may be useful later, but it would make release validation less deterministic and could obscure why a candidate received a label.

### Decision 2: Treat confidence as context, not promotion authority

High confidence can support a strong label only when evidence and provenance are also present. It cannot compensate for missing source refs or missing artifact provenance.

Alternative considered: allow high confidence to upgrade thin evidence. That would make the UI easier to satisfy but would weaken the accepted-baseline trust boundary.

### Decision 3: Improve partial candidates instead of hiding them

Partial candidates can be useful review inputs, so this slice should explain what is present and what is missing instead of filtering them out. Thin candidates should remain visible as diagnostics but be clearly bounded.

Alternative considered: suppress thin or partial candidates from review. That would reduce noise, but it could hide useful evidence about extraction gaps and make benchmark diagnosis harder.

### Decision 4: Keep reporting aligned with review labels

Benchmark and quality reports should use the same labels and reasons that reviewers see in the product. This avoids one quality model for UI and another for validation.

Alternative considered: maintain separate benchmark-only quality metrics. That would increase drift between product behavior and validation evidence.

## Risks / Trade-offs

- Risk: Tightened labels reduce the number of `strong` candidates in fixtures. Mitigation: adjust expectations only where the stricter label better reflects actual evidence quality.
- Risk: Review cards become noisy. Mitigation: keep visible reasons compact and push detailed diagnostics to tests/reports where possible.
- Risk: Deterministic quality labels remain heuristic. Mitigation: document the heuristic in the quality report and treat it as calibration input, not ground truth.
- Risk: Benchmark output becomes harder to stabilize if it depends on live providers. Mitigation: keep default CI fixture-based and live validation operator-guided.
