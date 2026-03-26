## Why

Real imported-workspace analysis now fails less often, but it still spends too long in `extracting_decisions` and too often burns expensive LLM calls on weak artifacts. This is now the main bottleneck between a successful import and a reviewable workspace, so improving extraction throughput and visibility is more urgent than further indexing or answer-polish work.

## What Changes

- Thin the extraction funnel so fewer low-value artifacts reach expensive full JSON extraction.
- Introduce a lightweight decision-likeness screening stage before full candidate extraction.
- Reduce extraction payload size by preferring more relevant sections over large raw artifact truncation.
- Add bounded extraction concurrency and richer extraction telemetry so long-running imports are faster and easier to interpret.
- Expose extraction progress details to live-analysis job status, including processed counts and ETA while extraction is running.

## Capabilities

### New Capabilities
- `decision-extraction-throughput`: governs the staged extraction funnel, extraction payload shaping, bounded throughput, and extraction telemetry for imported workspaces.

### Modified Capabilities
- `live-repository-analysis`: live-analysis progress reporting will include detailed extraction progress and richer extraction-stage summaries during long-running imports.

## Impact

- Affected code:
  - `services/engine/app/extractor/*`
  - `services/engine/app/jobs/import_jobs.py`
  - `services/engine/app/llm/*`
  - imported-workspace dashboard progress UI in `apps/web`
- Affected APIs:
  - import job status and dashboard summary payloads
- Affected systems:
  - live GitHub import pipeline
  - extraction provider usage, cost, and latency behavior
