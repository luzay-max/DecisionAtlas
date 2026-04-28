## Why

The v0.3 platform/access lanes are now in place, so the next release risk is whether real imported repositories produce decision candidates that reviewers can trust quickly. This change focuses the product back on decision value: fewer thin candidates, clearer review evidence, and a more natural path from first accepted baseline to why/drift usage.

## What Changes

- Improve the imported review queue so candidate summaries make decision value, provenance, confidence, and evidence strength easier to judge without opening every detail page.
- Add quality-oriented filtering or labeling for thin, low-value, or weakly grounded candidates so they do not look equivalent to strong imported decisions.
- Strengthen source-reference and artifact-provenance presentation where the data already exists.
- Make the first accepted imported baseline feel like a product milestone and expose the next why/drift entry points without overstating downstream trust.
- Update or add real-repository quality reporting so curated repository runs can capture candidate quality observations and follow-up risks.
- Keep implementation bounded: do not rewrite the extraction pipeline, introduce multiplayer review, or hard-code single-repository special cases.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `real-repository-outcomes`: Require real-repo validation/reporting to track decision-value quality and first-baseline usefulness, not only readiness state.
- `imported-review-decision-quality`: Require review surfaces to expose stronger candidate quality cues and clear low-value/thin-evidence signals.
- `source-ref-coverage`: Require source-ref coverage to support quality labeling and candidate review prioritization.
- `decision-extraction-conversion`: Require conversion diagnostics to distinguish reviewable decision value from merely valid structured output.
- `why-answer-support-grading`: Require post-acceptance why guidance to stay bounded by candidate quality and same-thread evidence.
- `lightweight-real-repo-benchmarks`: Require fixtures/reports to capture candidate-quality expectations and observed decision-value outcomes.

## Impact

- Web review queue and related imported workspace guidance.
- Engine/API review payloads, source-ref metadata, readiness/quality summaries, and benchmark/report generation.
- Tests around imported review cards, source-ref coverage, candidate quality labels, and why/drift post-acceptance guidance.
- Documentation/reporting under `docs/project` for real repository quality observations.
