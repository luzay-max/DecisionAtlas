# 2026-06-22 Update Log — Session 2 (mimo branch continuation)

## P5a: First-Run Onboarding Guidance

- Added "Getting Started" 4-step guide to homepage with descriptions for each step.
- Added "Next Steps" section with links to analyze repo, settings, and evidence pages.
- Added i18n messages for onboarding content in English and Chinese.
- Updated home-page test to handle duplicate text from onboarding section.
- Validation: typecheck passed, all 76 web tests passed.

## P5b: Dashboard Aggregated Entry Points

- Added governance and evidence navigation links to workspace dashboard action row.
- Dashboard now provides direct access to: Review, Why Search, Drift, Timeline, Governance, Evidence.
- Validation: all 76 web tests passed.

## P5c: Actionable Recovery Suggestions

- Updated all 7 error boundaries with step-by-step recovery guidance:
  - Root error: check services running, refresh, check console
  - 404: go home, check URL, use sidebar
  - Review: ensure workspace has data, check Engine running
  - Search: check accepted decisions, LLM provider, Engine
  - Timeline: check accepted decisions, Engine
  - Governance: check documents imported, Engine
  - Team: check API running, admin role
- Validation: typecheck passed, all 76 web tests passed.

## P6: Trend Comparison Wiring

- Added trend comparison as advisory signal in `collect_release_evidence.py`.
- Added `summarize_trend_comparison` to `collect_team_handoff_report.py`.
- Added `--trend-comparison-report` and `--trend-comparison-json` CLI arguments.
- Validation: scripts compile, all 54 CI tests pass.

## Full Test Suite Results

| Area | Test Files | Tests | Status |
|------|-----------|-------|--------|
| Web (vitest) | 20 | 76 | All passed |
| API (vitest) | 11 | 32 | All passed |
| Engine (pytest) | 56 | 294 | All passed |
| OpenSpec | 64 | 64 | All passed |
| **Total** | **151** | **466** | **All passed** |

## Files Created/Modified (Session 2)

- `apps/web/app/page.tsx` (modified — onboarding + next steps sections)
- `apps/web/app/error.tsx` (modified — recovery suggestions)
- `apps/web/app/not-found.tsx` (modified — recovery suggestions)
- `apps/web/app/review/error.tsx` (modified — recovery suggestions)
- `apps/web/app/drift/error.tsx` (modified — recovery suggestions)
- `apps/web/app/search/error.tsx` (modified — recovery suggestions)
- `apps/web/app/timeline/error.tsx` (modified — recovery suggestions)
- `apps/web/app/governance/error.tsx` (modified — recovery suggestions)
- `apps/web/app/team/error.tsx` (modified — recovery suggestions)
- `apps/web/components/dashboard/workspace-dashboard-content.tsx` (modified — governance/evidence links)
- `apps/web/components/i18n/messages.ts` (modified — onboarding i18n)
- `apps/web/tests/home-page.test.tsx` (modified — fix duplicate text)
- `scripts/ci/collect_release_evidence.py` (modified — trend comparison source)
- `scripts/ci/collect_team_handoff_report.py` (modified — trend comparison section)
