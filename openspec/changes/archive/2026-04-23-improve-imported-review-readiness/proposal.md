## Why

Imported workspaces now reach reviewable candidate decisions more often, but many real repositories still stall before the first accepted baseline is established. That leaves the product in a fragile middle state where review exists, but why and drift remain hard to trust or hard to act on.

## What Changes

- Tighten imported-workspace readiness so product surfaces distinguish between "candidate review is available now" and "an accepted baseline is established now".
- Improve imported review flow guidance so the dashboard and related surfaces steer users toward the first high-value acceptance instead of treating all review-ready states as equivalent.
- Improve imported why readiness after the first accepted decision so the product can expose a clearer step-up from review-only to grounded why usage.
- Extend lightweight benchmark expectations to protect first-accepted-decision readiness and the resulting imported why/readiness contract on curated real repositories.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `imported-workspace-readiness-surface`: refine imported readiness states and recommended actions around first accepted-decision progress.
- `real-repository-outcomes`: define first accepted decision as a meaningful imported outcome milestone and tighten how review, why, and drift progression is summarized.
- `why-answer-support-grading`: reflect the stronger why-readiness expectations that follow the first accepted imported baseline.
- `lightweight-real-repo-benchmarks`: protect imported review-readiness and first-accepted-baseline expectations with fixture-backed benchmark cases.

## Impact

- Affected code: imported workspace readiness evaluation, dashboard/search imported summaries, review-to-why product routing, benchmark fixtures and validation.
- Affected APIs: dashboard summary and why response contracts where imported readiness/support state is surfaced.
- Affected systems: web imported-lane UX, engine readiness/outcome modeling, fixture-backed benchmark validation.
