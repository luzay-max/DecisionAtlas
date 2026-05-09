## Context

DecisionAtlas now produces three important evidence families:

- release evidence bundles from `scripts/ci/collect_release_evidence.py`
- hosted/operator readiness bundles from `scripts/demo/collect_hosted_readiness.py`
- real-repo benchmark snapshots and comparison reports from `scripts/ci/run_benchmark.py`

These files are currently generated in `.tmp/`, which is correct for scratch output but weak as a release or preview memory layer. Operators need a deliberate way to promote selected evidence into durable history, compare recent entries, and reference evidence without committing stale temporary files accidentally.

## Goals / Non-Goals

**Goals:**
- Add a local command to archive selected readiness evidence into a durable dated/versioned directory.
- Store release evidence, hosted readiness evidence, benchmark comparison evidence, and their Markdown handoffs as linked evidence sets.
- Maintain an index file that summarizes each evidence entry with status, commit/version label, source paths, warnings, blockers, and benchmark movement counts.
- Provide a trend summary command that compares recent evidence entries without running live checks.
- Keep the workflow explicit: operators choose when `.tmp` evidence becomes durable history.
- Preserve non-mutating defaults and avoid introducing hosted state management.

**Non-Goals:**
- Do not automatically commit `.tmp` outputs.
- Do not run canonical pre-release, hosted smoke, live benchmark, reset, reseed, or import commands as part of history archiving.
- Do not add a database table, hosted dashboard, release approval workflow, or CI enforcement.
- Do not store secrets, private repository content, raw model output, or local-only absolute paths as required durable evidence.

## Decisions

### Durable Directory Convention
Use a predictable docs-owned history location, for example:

```text
docs/evidence/readiness/<YYYY-MM-DD>-<label>/
```

Each entry should contain copied evidence artifacts and an `entry.json` summary. A top-level `docs/evidence/readiness/index.json` should summarize all entries.

### Explicit Promotion From `.tmp`
The history command should require explicit source paths for release evidence, hosted readiness, and benchmark comparison artifacts. If a source is omitted, the entry records that evidence as not provided. It must not scan `.tmp` broadly or silently pick the newest matching file.

### Stable Index Before Rich UI
The first implementation should use JSON and Markdown files only. This keeps the history reviewable in git and avoids building a dashboard before evidence format stabilizes.

### Trend Summary Is Offline
Trend summaries should read committed or locally available history entries only. They should not run live checks or depend on hosted URLs, GitHub, providers, or a running stack.

### Preserve Evidence Boundaries
Release evidence, hosted readiness, and benchmark comparison remain different evidence families. The history index can summarize them together, but it must not collapse advisory/operator-guided states into a false pass.

## Risks / Trade-offs

- **Risk: committing sensitive evidence.** Mitigation: document that raw secrets, private repo contents, raw model output, and local-only logs should not be archived; store summaries and selected reports only.
- **Risk: stale `.tmp` files becoming durable by accident.** Mitigation: require explicit paths and record original source paths plus generated timestamps.
- **Risk: history becomes noisy.** Mitigation: use operator-provided labels and keep one entry per release, preview, or meaningful validation event.
- **Risk: trend summaries overclaim readiness.** Mitigation: preserve exact statuses and show operator-guided, warning, blocking, and not-provided states explicitly.
- **Trade-off: docs-backed history over database storage.** Git-tracked docs are simpler and auditable for the current repo maturity stage; a database-backed evidence UI can come later if needed.
