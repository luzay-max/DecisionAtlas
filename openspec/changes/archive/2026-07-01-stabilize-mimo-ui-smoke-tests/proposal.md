## Why

The `mimo` branch added global sidebar/onboarding UI surfaces, but page-level tests can fail when isolated components render `GlobalSidebar` without the full theme provider tree. The branch also needs a repeatable browser smoke path that proves the new homepage, settings, evidence, 404, and demo workspace navigation remain usable.

## What Changes

- Stabilize review, drift, and timeline component tests by isolating global sidebar/navigation dependencies from page-content assertions.
- Add a Mimo UI Playwright smoke covering homepage onboarding, quick actions, settings, evidence, 404 recovery, and demo workspace flow.
- Record the dependency/setup requirements needed to run the smoke reliably on the `mimo` branch.
- Preserve existing product behavior; this change is test and verification coverage, not a user-facing UI redesign.

## Capabilities

### New Capabilities
- `mimo-ui-smoke-coverage`: Browser and component-test coverage for the `mimo` branch UI shell, onboarding, sidebar navigation, evidence/settings surfaces, and demo workspace flow.

### Modified Capabilities
- None.

## Impact

- Affected tests:
  - `apps/web/tests/review-page.test.tsx`
  - `apps/web/tests/drift-page.test.tsx`
  - `apps/web/tests/timeline-page.test.tsx`
  - `apps/web/tests-e2e/mimo-ui-smoke.spec.ts`
- Affected verification:
  - Vitest page-content tests for review/drift/timeline.
  - Playwright smoke against local Web/API/Engine smoke servers.
- No API, database, or production runtime behavior changes are intended.
