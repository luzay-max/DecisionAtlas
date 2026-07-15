## Context

The `mimo` branch introduces a broader UI shell with global sidebar navigation, onboarding guidance, settings/evidence pages, and demo workflow surfaces. Existing page-content component tests render review, drift, and timeline content directly; once those components include `GlobalSidebar`, isolated tests can accidentally exercise theme/navigation behavior instead of the page content under test.

The branch also needs a browser smoke that proves the new top-level UI path still works when Web/API/Engine smoke servers are started through the Playwright config.

## Goals / Non-Goals

**Goals:**
- Keep review, drift, and timeline page-content tests focused on their own content and API interactions.
- Verify Mimo UI shell pages in Chromium through Playwright.
- Document the proxy/dependency assumptions needed for reliable local e2e execution.
- Preserve the current product behavior on the `mimo` branch.

**Non-Goals:**
- Redesign global sidebar, theme provider, or page layout.
- Add new runtime APIs, database migrations, or production dependencies.
- Replace existing `demo-smoke` or team self-hosted rehearsal tests.
- Claim complete release readiness from this smoke alone.

## Decisions

- Mock `GlobalSidebar` in page-content unit tests rather than wrapping every page-content test in the full app provider tree. This keeps these tests scoped to review/drift/timeline behavior and avoids duplicating app-shell integration setup in many unit tests.
- Keep sidebar/theme integration covered by Playwright smoke instead of by every component unit test. This catches real browser failures while preserving focused unit tests.
- Run Playwright with local Web/API/Engine smoke servers and with localhost proxy bypass. The local environment may define `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY`; e2e commands must clear those variables for localhost checks when needed.
- Treat package dependency linking as a prerequisite. `apps/web` and `apps/api` must have workspace dependencies linked before Playwright can resolve `@playwright/test` and `tsx`.

## Risks / Trade-offs

- Mocking `GlobalSidebar` in component tests could hide sidebar integration regressions -> Mitigate through browser smoke that renders the real sidebar.
- Playwright webServer can mis-detect localhost availability when proxy variables point at an invalid proxy -> Mitigate by clearing proxy variables for local smoke commands.
- The smoke uses seeded/demo data and mocked why-search response for one route -> Mitigate by keeping real repository validation as a separate release evidence lane.
- This change improves regression coverage but does not prove the whole `mimo` branch is production-ready -> Mitigate by recording this limitation in the update log and keeping broader release evidence separate.
