## Context

Current real random repository evidence uses `n8n` and `rich`. Both repositories import/open enough for setup and dashboard pass, but core-loop evidence remains warning because review, why-search, drift, and guardrail lanes are not fully clean. The new warning reducer then identifies three product-controlled lanes:

- Full-chain multi-repo diagnosis aggregate.
- Release rehearsal benchmark comparison aggregate.
- Release rehearsal multi-repo diagnosis aggregate.

The benchmark comparison warning is not a product quality issue; the source comparison has `release_evidence_ready: true`, no regressions, and no operational blockers, but the release rehearsal summarizer reads no explicit top-level status and reports `unknown`.

## Goals / Non-Goals

**Goals:**
- Make benchmark comparison summary status deterministic from bounded comparison metrics.
- Preserve warning status for real incomplete core-loop evidence, but classify why it is incomplete.
- Expose `product_action_count` and `operator_action_count` so release evidence can prioritize real product work.
- Regenerate warning-lane reduction evidence to prove fewer lanes are incorrectly product-controlled.

**Non-Goals:**
- Do not mark repositories as pass while review/why/drift/guardrail evidence remains incomplete.
- Do not require an LLM/model call.
- Do not hard-code repository-specific success for `n8n` or `rich`.
- Do not add new UI or account-management behavior.

## Decisions

1. Derive benchmark comparison status from summary metrics.
   - If `regressed` or `operationally_blocked` is non-zero, status remains warning.
   - If `release_evidence_ready` is true and there are no regressions/blockers, status is pass.
   - Otherwise status remains warning/unknown.

2. Add action categories to core-loop lanes.
   - Product categories cover review quality, why grounding, drift evaluation, and guardrail evidence.
   - Operator categories cover waiting for import, missing workspace/setup, and manually supplied proof.

3. Aggregate action categories in multi-repo diagnosis.
   - The aggregate can still be warning, but downstream evidence can tell whether the next step is product improvement or operator/setup completion.

4. Teach warning-lane reduction to honor action-category summaries.
   - Product-controlled classification should require a positive product action count that is not dominated by operator setup.

## Risks / Trade-offs

- A warning may move from product-controlled to operator-guided even though the product could still improve asynchronous import completion -> keep source warning visible and include both counts.
- Existing smoke evidence may still be warning after the fix -> acceptable; the goal is better attribution, not fake pass.
- Deriving benchmark comparison status could hide missing baseline rows -> only pass when release evidence explicitly says ready and no regressions/blockers exist.

## Migration Plan

Update scripts and tests, regenerate current `.tmp` evidence, archive a new readiness history entry, then archive the OpenSpec change. Existing evidence files remain compatible because new fields are additive.
