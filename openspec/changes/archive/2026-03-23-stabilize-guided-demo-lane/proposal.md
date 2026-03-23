## Why

The MVP already demonstrates the core product capabilities, but the public walkthrough still behaves like a mixed product console instead of a guided demo. Users can reach the right pages, yet the current flow makes them decide too much, exposes advanced controls too early, and still leaves room to confuse seeded demo output with experimental live-analysis behavior.

## What Changes

- Introduce a guided-demo experience that presents the demo workspace as the primary walkthrough with a clear ordered flow from dashboard to review, why-search, timeline, and drift.
- Add explicit progress, next-step cues, and completion states so the walkthrough feels like one connected experience instead of a collection of pages.
- Reframe live analysis and provider switching as advanced or experimental controls rather than primary homepage and workspace actions.
- Extend provenance and expectation-setting copy so review, homepage, and advanced entry points make the demo boundary obvious.

## Capabilities

### New Capabilities
- `guided-demo-experience`: Defines the stable guided walkthrough, step progression, next actions, and advanced-control demotion needed for the MVP demo lane.

### Modified Capabilities
- `data-provenance-labeling`: Expand provenance expectations so review surfaces and advanced-entry copy clearly distinguish seeded walkthrough behavior from imported or experimental analysis.

## Impact

- `apps/web` homepage, demo navigation, dashboard, review, why-search, timeline, and drift UI flows
- Demo-focused copy, messaging, and walkthrough status presentation
- Potential small API read-model additions only if needed to support demo progress state without relying on user inference
