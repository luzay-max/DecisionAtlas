## Context

The live benchmark uses a source-controlled repository profile with `expected_value_outcomes`. The current evaluator requires the observed value outcome to be an exact member of that list. This is safe against silent changes but fails when the product improves beyond the profile's original stress expectation. The n8n profile currently produces `useful_now` even though its original expectation stopped at `reviewable_limited` and other bounded limitations.

The change is limited to benchmark/reporting semantics. Product runtime readiness, candidate quality gates, Why/Drift case gates, and operational failure handling remain independent checks.

## Goals / Non-Goals

**Goals:**

- Treat ranked product outcomes as a minimum floor when a benchmark profile lists one or more ranked product outcomes.
- Preserve exact handling for `missing_workspace` and `operational_blocked` so infrastructure failures cannot be promoted into product improvements.
- Emit a bounded assessment explaining whether an observed outcome is an exact match or exceeds the configured floor.
- Add tests for improvement, regression, operational outcomes, and profiles with no product floor.

**Non-Goals:**

- Do not alter the product's workspace readiness state or acceptance workflow.
- Do not lower candidate-quality, Why, Drift, screened-in, or import success thresholds.
- Do not add repository-specific exceptions for n8n or any other benchmark profile.
- Do not infer a pass from missing data, network errors, or absent workspaces.

## Decisions

1. **Use the existing value rank as a product floor.** `VALUE_OUTCOME_RANK` already orders `conversion_limited`, `evidence_limited`, `reviewable_limited`, and `useful_now`. The observed outcome is acceptable when its rank is at least the lowest configured product-value expectation. This keeps a profile's weakest declared product state as its minimum bar while allowing a better result.

2. **Keep operational outcomes outside the rank.** `missing_workspace` and `operational_blocked` are not product quality levels. They remain exact, non-promotable outcomes even if a profile also lists product states.

3. **Expose the assessment in bounded JSON.** Add an assessment such as `exact`, `exceeds_floor`, `below_floor`, `operational`, or `not_constrained`, plus the configured floor. This makes benchmark evidence explain why a row passed without embedding generated prose.

4. **Test the pure report path and a live-style row.** Unit tests will exercise `_attach_value_summary` directly and the existing live validation fake-request path, so the rule is verified without depending on a provider or repository network call.

## Risks / Trade-offs

- [Risk] A profile may declare an overly weak product floor and accept a mediocre outcome. -> Mitigation: keep profile expectations source-controlled, preserve candidate/Why/Drift gates, and review benchmark trend movement separately.
- [Risk] Rank ordering may be misunderstood by future maintainers. -> Mitigation: name the field `minimum_product_value_floor` and emit the assessment explicitly.
- [Risk] Operational states could accidentally enter the product rank. -> Mitigation: explicit operational branch and regression tests for missing workspace and network failure.

## Migration Plan

No data migration is required. Deploy the evaluator and tests, rerun the fixed live benchmark, regenerate comparison/release evidence, and confirm that improved rows are marked `exceeds_floor`. Rollback is a code revert if the assessment changes unexpectedly; no persisted product data is modified.

## Open Questions

- Whether future benchmark profiles should declare a single floor instead of a list can be revisited after more release history exists; this change keeps the existing list format for compatibility.
