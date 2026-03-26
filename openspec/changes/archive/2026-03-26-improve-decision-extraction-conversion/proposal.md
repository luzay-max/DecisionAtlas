## Why

The previous throughput work made imported extraction faster and more observable, but recent real-repository tests still showed a poor `screened-in -> candidate` conversion rate, including runs where dozens of full extraction requests produced zero reviewable candidates. That means the next bottleneck is no longer throughput alone, but the quality and resilience of the full extraction step itself.

## What Changes

- Improve full extraction quality so screened-in artifacts are more likely to become reviewable candidate decisions instead of collapsing to `null`, invalid JSON, or missing-field failures.
- Introduce artifact-family-aware extraction behavior for rationale-bearing docs, PRs, and lighter-weight issue/commit evidence instead of relying on one prompt shape for every artifact.
- Add conversion diagnostics so imported runs can explain why screened-in artifacts failed to become candidates.
- Surface low-yield extraction outcomes in imported workspace summaries so users can distinguish “repo evidence is weak” from “full extraction is not converting”.
- Expand benchmark-style validation around candidate yield, not just throughput and progress visibility.

## Capabilities

### New Capabilities
- `decision-extraction-conversion`: governs artifact-aware extraction, candidate salvage rules, and diagnostics for screened-in artifacts that fail to convert into candidate decisions

### Modified Capabilities
- `real-repository-outcomes`: imported workspace read models will explain low-yield extraction runs using conversion diagnostics rather than only a generic evidence-limited outcome

## Impact

- Affected code:
  - `services/engine/app/extractor/*`
  - `services/engine/app/llm/*`
  - `services/engine/app/jobs/import_jobs.py`
  - imported-workspace dashboard and readiness UI in `apps/web`
- Affected APIs:
  - import job summary payloads
  - dashboard summary payloads for imported workspaces
- Affected systems:
  - full extraction prompt strategy
  - parser and candidate persistence behavior
  - imported workspace outcome diagnostics and benchmark evaluation
