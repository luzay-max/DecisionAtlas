# 2026-06-22 Update Log (mimo branch)

## Error Boundaries (P5-UI-P1)

- Added Next.js error boundaries to root and 6 route-specific directories:
  - `apps/web/app/error.tsx` — global error boundary
  - `apps/web/app/loading.tsx` — global loading spinner
  - `apps/web/app/not-found.tsx` — 404 page
  - `apps/web/app/review/error.tsx`
  - `apps/web/app/drift/error.tsx`
  - `apps/web/app/search/error.tsx`
  - `apps/web/app/timeline/error.tsx`
  - `apps/web/app/governance/error.tsx`
  - `apps/web/app/team/error.tsx`
- Each error boundary includes retry and home navigation actions.
- Validation: typecheck passed, all 76 web tests passed.

## Global Navigation Sidebar (P5-UI-P2)

- Added `apps/web/components/navigation/global-sidebar.tsx` with fixed-position sidebar.
- Navigation links: Home, Review, Why Search, Timeline, Drift, Governance, Team, Settings, Evidence.
- Active link highlighting based on current pathname.
- Account scope, language toggle, and theme toggle in sidebar footer.
- Added responsive CSS (hidden on screens < 768px).
- Light and dark theme support.
- Added i18n messages for governance, team, settings, evidence in both English and Chinese.
- Validation: typecheck passed, all 76 web tests passed.

## Settings Page (P5-UI-P4)

- Added `apps/web/app/settings/page.tsx` with:
  - LLM Provider mode toggle
  - System status (Engine, Gateway, Web UI URLs)
  - Database status (PostgreSQL)
  - Cache & Queue status (Redis)
- Added `apps/web/tests/settings-page.test.tsx` — 1 test passed.

## Evidence Page (P5-UI-P5)

- Added `apps/web/app/evidence/page.tsx` with:
  - Governance guardrail status display
  - Available CLI report commands
  - Self-hosted package build/verify commands
- Added `apps/web/tests/evidence-page.test.tsx` — 2 tests passed.

## OpenSpec Spec Purpose Fixes

- Fixed 9 specs with TBD purpose headers:
  - `self-hosted-commercial-baseline`
  - `self-hosted-delivery-rehearsal`
  - `readiness-evidence-history`
  - `release-evidence-automation`
  - `hosted-operator-delivery-readiness`
  - `guided-demo-experience`
  - `v0-3-real-stack-validation`
  - `v0-3-release-candidate-baseline`
  - `data-provenance-labeling`
- Validation: `openspec validate --all --strict`: 64 passed, 0 failed.

## Automated Trend Comparison (P6)

- Added `scripts/ci/compare_release_trends.py` for automated trend comparison between releases.
- Compares current benchmark metrics against previous readiness evidence.
- Generates JSON and Markdown trend comparison reports.
- Classifies movements: improved, regressed, unchanged, first-measurement, missing-from-current.
- Advisory status (does not block releases by default).
- Validation: script compiles and runs successfully.

## Full Test Suite Results

| Area | Test Files | Tests | Status |
|------|-----------|-------|--------|
| Web (vitest) | 20 | 76 | All passed |
| API (vitest) | 11 | 32 | All passed |
| Engine (pytest) | 56 | 294 | All passed |
| OpenSpec | 64 | 64 | All passed |
| **Total** | **151** | **466** | **All passed** |

## Files Created/Modified

- `apps/web/app/error.tsx` (new)
- `apps/web/app/loading.tsx` (new)
- `apps/web/app/not-found.tsx` (new)
- `apps/web/app/review/error.tsx` (new)
- `apps/web/app/drift/error.tsx` (new)
- `apps/web/app/search/error.tsx` (new)
- `apps/web/app/timeline/error.tsx` (new)
- `apps/web/app/governance/error.tsx` (new)
- `apps/web/app/team/error.tsx` (new)
- `apps/web/app/settings/page.tsx` (new)
- `apps/web/app/evidence/page.tsx` (new)
- `apps/web/components/navigation/global-sidebar.tsx` (new)
- `apps/web/app/globals.css` (modified — sidebar CSS)
- `apps/web/components/i18n/messages.ts` (modified — nav i18n)
- `apps/web/tests/global-sidebar.test.tsx` (new)
- `apps/web/tests/settings-page.test.tsx` (new)
- `apps/web/tests/evidence-page.test.tsx` (new)
- `scripts/ci/compare_release_trends.py` (new)
- 9 OpenSpec spec files (modified — purpose headers)

## Branch

- Branch: `mimo`
- Not merged to main.
