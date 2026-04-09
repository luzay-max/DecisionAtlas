## Why

Imported workspaces now expose useful underlying states such as `review_ready`, `why_ready`, `evidence_limited`, `conversion_limited`, and drift evaluation status. But that readiness is still presented mostly as a thin card plus scattered links across dashboard, search, and drift surfaces.

In practice, users can still end up asking:

- Is this workspace ready for review, why-search, or drift?
- Why am I being sent to review from one place and why from another?
- Is this an evidence problem, a conversion problem, or simply that I should reuse the workspace as-is?

The current surface exposes the raw state, but not a cohesive "what can I do now?" view.

## What Changes

- Build a clearer imported-workspace readiness surface that summarizes:
  - overall readiness state
  - why readiness
  - drift readiness
  - strongest next action
- Make dashboard and search surfaces render the same readiness language instead of partially repeating guidance.
- Expose enough structured readiness detail in the API contract for UI surfaces to render richer imported-workspace guidance without inventing local heuristics.

## Expected Outcome

- Imported workspaces feel more productized and less like raw state dumps.
- Users can tell whether they should review, ask why, inspect drift, or inspect import limitations.
- The product communicates "what this workspace is ready for now" consistently across screens.
