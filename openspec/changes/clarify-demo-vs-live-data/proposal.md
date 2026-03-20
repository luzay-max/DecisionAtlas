## Why

DecisionAtlas currently mixes seeded demo content and real imported repository content without making that distinction explicit in the product. This creates trust risk: users can misread seeded timeline, why-answer, and drift results as proof of live repository analysis when they are actually looking at stable demo data.

## What Changes

- Add explicit workspace-level provenance so the product can label a workspace as `demo`, `imported`, or `mixed`.
- Expose provenance summary data through the dashboard and related read APIs used by the main demo flow.
- Update the dashboard, why search, timeline, drift, and decision detail experiences to explain whether the user is viewing seeded demo data or imported repository data.
- Clarify homepage and demo-facing copy so the public demo no longer blurs seeded walkthrough data with real import behavior.

## Capabilities

### New Capabilities
- `data-provenance-labeling`: Label workspace data origin in the UI and API so users can tell whether content comes from seeded demo data, imported repository data, or a mixed state.

### Modified Capabilities
- None.

## Impact

- Affected code: `apps/web/app/page.tsx`, dashboard/search/timeline/drift/decision-detail components, `apps/web/lib/api.ts`
- Affected APIs: dashboard summary, why query, timeline, drift alerts, decision detail
- Affected systems: demo workspace presentation, imported workspace presentation, documentation and demo script copy
