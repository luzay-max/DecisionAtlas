## Scope

This change improves how imported-workspace readiness is surfaced. It does not redefine the underlying readiness model from scratch and does not introduce new decision extraction, why-search, or drift logic.

In scope:

- richer readiness payload shape for imported workspaces
- one consistent mapping from backend readiness to UI guidance
- dashboard/search imported surfaces using the same readiness framing

Out of scope:

- changing how candidate/accepted/drift states are computed
- redesigning live import orchestration
- adding new extraction or drift classifications

## Design

### 1. Readiness becomes a small structured summary

The current readiness payload exposes:

- `state`
- `next_action`
- `why_state`
- `drift_state`

That is enough for routing, but not enough for a product-quality explanation surface. The payload should grow into a compact summary with:

- `state`
- `next_action`
- `why_state`
- `drift_state`
- `headline`
- `detail`
- `recommended_actions`

The backend remains the source of truth for this summary so dashboard/search do not drift into separate heuristics.

### 2. Recommended actions are explicit, not inferred

Imported readiness should explicitly recommend a small set of allowed actions such as:

- `review_candidates`
- `ask_why`
- `evaluate_drift`
- `inspect_import_summary`

The primary `next_action` remains the strongest recommendation. `recommended_actions` allows the UI to show secondary paths without inventing them per page.

### 3. Dashboard and search use the same imported readiness block

Dashboard currently has the clearest imported-state context. Search currently shows the readiness card but still reads like an isolated why surface. This change makes both use one richer readiness block so the user sees:

- what the workspace is ready for
- why that is the current state
- what to do next

### 4. Readiness guidance stays operational

The surface should continue distinguishing:

- `review_ready`
- `why_ready`
- `evidence_limited`
- `conversion_limited`
- `analysis_failed`

It should also make drift readiness legible without forcing the user onto the drift page first.

## Validation

Validation should cover:

- backend readiness payload for representative imported workspace states
- dashboard rendering for review-ready / why-ready / limited states
- search rendering for imported workspaces with richer readiness context
