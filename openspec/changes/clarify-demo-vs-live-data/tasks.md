## 1. Backend provenance context

- [x] 1.1 Add workspace-level provenance classification logic in the engine for `demo`, `imported`, and `mixed` modes.
- [x] 1.2 Extend dashboard summary, why query, timeline, drift, and decision detail responses with provenance summary fields needed by the UI.
- [x] 1.3 Add or update backend tests covering provenance classification and provenance-aware API responses.

## 2. Frontend provenance presentation

- [x] 2.1 Extend shared web API types in `apps/web/lib/api.ts` to include provenance fields returned by backend read APIs.
- [x] 2.2 Update dashboard, why search, timeline, drift, and decision detail pages to display workspace provenance and source summaries.
- [x] 2.3 Update homepage and demo-facing copy so the public demo clearly distinguishes seeded walkthrough behavior from real imported workspace behavior.

## 3. Validation and rollout

- [x] 3.1 Add web tests for demo/imported provenance labels on the main trust-sensitive pages.
- [x] 3.2 Run web typecheck, web tests, and any affected engine/API tests to confirm provenance labeling does not break the current demo path.
- [x] 3.3 Update progress tracking and any relevant demo documentation after provenance labeling is complete.
