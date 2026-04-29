## Why

The v0.3 RC proves that real repositories can produce reviewable imported decisions, but the next product bottleneck is whether those candidates are actually useful enough for a reviewer to accept as the first durable baseline. The system already exposes candidate quality signals; this change tightens and clarifies those signals so strong, partial, and thin candidates are easier to judge without rewriting the extraction pipeline.

## What Changes

- Calibrate imported candidate quality labels so `strong`, `partial`, and `thin` have clearer evidence boundaries.
- Make review cards explain why a candidate received its quality label, with compact source-ref, quote, provenance, and confidence cues.
- Improve real-repository quality reporting so benchmark and operator output shows label distribution and thin-candidate pressure in a reviewer-useful way.
- Add tests for boundary cases where confidence is high but evidence/provenance is weak, and where partial candidates should not be mislabeled as strong.
- Update the real-repository quality report with the calibrated quality model and current limits.
- Do not change the main LLM extraction prompt or pipeline in this slice.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `imported-review-decision-quality`: tighten imported review-card quality cues and require review-visible reasons for strong/partial/thin labels.
- `real-repository-outcomes`: strengthen real-repository outcome reporting so candidate value observations include label distribution, thin pressure, and first-baseline usefulness.
- `source-ref-coverage`: clarify how source-ref count, previewable quote availability, and provenance gaps support candidate quality labels.

## Impact

- Engine API serialization for imported decisions:
  - `services/engine/app/api/decisions.py`
- Review UI and copy:
  - `apps/web/components/review/review-list.tsx`
  - `apps/web/components/i18n/messages.ts`
- Real-repository benchmark/reporting:
  - `scripts/ci/run_benchmark.py`
  - benchmark fixture expectations if needed
- Documentation:
  - `docs/project/real-repo-decision-quality-report.md`
- Tests:
  - engine decision API tests
  - web review-page tests
  - benchmark fixture validation tests
