## Context

Imported-workspace analysis currently runs:

```text
import artifacts
  -> index artifacts
  -> extract candidate decisions
  -> review
  -> accepted decisions
  -> why / timeline / drift
```

The current extraction stage is too blunt:

- shortlist heuristics are broad enough that many merely-possible artifacts enter extraction
- every selected artifact goes straight to a full structured extraction request
- extraction inputs can be very large
- provider calls are effectively serial
- progress reporting shows that extraction is running, but not how much work remains

This makes imported-workspace analysis feel slow and opaque precisely at the point where the product is supposed to become useful.

## Goals / Non-Goals

**Goals:**

- Reduce the number of full extraction calls made per imported repository run.
- Reduce wall-clock time spent in `extracting_decisions`.
- Preserve or improve reviewable candidate quality while thinning the funnel.
- Surface enough live extraction telemetry for operators to tell whether progress is real or stalled.
- Keep the change focused on extraction throughput, not broad retrieval redesign.

**Non-Goals:**

- Redesign why-search retrieval or answer generation.
- Redesign indexing, chunking, or artifact-chunk retrieval.
- Introduce multimodal extraction or model-routing infrastructure.
- Rework review UI beyond using richer import progress data.

## Decisions

### Decision: Split extraction into a two-stage funnel

The pipeline will move from:

```text
shortlist -> full JSON extraction
```

to:

```text
strict shortlist
  -> lightweight decision-likeness screening
  -> full JSON extraction for screened positives only
```

Why:

- the current design uses the most expensive LLM step too early
- many shortlisted artifacts are not truly decision-bearing
- a cheap first pass can cut cost and wall-clock time substantially

Alternatives considered:

- keep one-stage extraction and only tighten heuristics
  - rejected because heuristics alone are brittle and still force expensive calls too often
- replace heuristics with embedding-based prefiltering first
  - rejected because it expands scope into indexing and retrieval quality work

### Decision: Make shortlist scoring more selective before any LLM call

The shortlist will be tightened to favor rationale-bearing artifacts such as ADRs, RFCs, architecture docs, migration docs, rollout docs, and high-signal PR descriptions, while lowering the priority of generic issues, short commits, and broad README content.

Why:

- the easiest way to improve throughput is to reduce low-value calls
- the current `score > 0` threshold is too permissive for repository-scale imports

Alternatives considered:

- keep the shortlist broad and rely only on screening
  - rejected because it still creates too many provider calls in large repositories

### Decision: Reduce extraction payloads by selecting relevant sections

Instead of sending large head/tail truncations, extraction inputs will prefer title, path, headings, and the most relevant rationale-bearing paragraphs or sections.

Why:

- full documents are often much larger than the actual decision-bearing region
- smaller, more relevant payloads reduce latency and timeout risk

Alternatives considered:

- only lower the global max character limit
  - rejected because blunt truncation still risks discarding the useful section

### Decision: Add bounded concurrency only after the funnel is thinner

Extraction calls will remain bounded to a small concurrency level rather than becoming fully parallel.

Why:

- sequential execution wastes wall-clock time
- very high concurrency would amplify provider rate-limit and debugging risks
- keeping database writes coordinated is simpler when extraction results are collected and persisted in a controlled way

Alternatives considered:

- fully serial execution
  - rejected because it keeps the main throughput bottleneck intact
- aggressive high concurrency
  - rejected because it is too risky for provider stability and observability

### Decision: Report funnel telemetry through import summaries

Import job summary data will report extraction funnel statistics such as shortlisted artifacts, screened artifacts, full extraction requests, processed counts, candidate creations, timeout counts, and ETA-friendly progress data.

Why:

- users currently cannot tell whether extraction is genuinely progressing
- the team needs metrics to compare throughput changes across benchmark repositories

Alternatives considered:

- keep only stage-level progress
  - rejected because it is insufficient for long-running extraction work

## Risks / Trade-offs

- **[Risk] Screening becomes too strict and suppresses real decisions** → Mitigation: benchmark against the curated repository set and measure created/accepted candidate counts before and after.
- **[Risk] Two-stage extraction increases complexity and prompt maintenance** → Mitigation: keep the screening output intentionally small and tightly scoped.
- **[Risk] Bounded concurrency can still trigger provider instability** → Mitigation: start with a low concurrency cap and expose timeout/rate-limit counts in telemetry.
- **[Risk] More telemetry increases payload complexity** → Mitigation: keep telemetry fields focused on counts and durations already needed by UI and benchmarks.

## Migration Plan

1. Introduce the stricter shortlist and screening stage behind the existing imported-workspace flow.
2. Add extraction telemetry to import summaries without breaking current stage names.
3. Update imported-workspace progress UI to consume the richer extraction summary.
4. Validate the benchmark repository set for:
   - import duration
   - extraction request counts
   - candidate counts
   - accepted-decision readiness
5. If throughput improves but recall regresses too far, loosen shortlist or screening thresholds before wider rollout.

## Open Questions

- Should screening use the same model as full extraction or a smaller, cheaper model abstraction later?
- What shortlist cap should apply per repository before screening begins?
- Should ETA be based on processed artifacts only, or split into screened vs full-extracted counts for more stable estimates?
