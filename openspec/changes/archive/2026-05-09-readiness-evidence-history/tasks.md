## 1. Evidence History Shape

- [x] 1.1 Review release evidence, hosted readiness, and benchmark comparison JSON/Markdown output shapes.
- [x] 1.2 Define the durable history directory convention and entry naming rules.
- [x] 1.3 Define the entry summary schema and top-level history index schema.
- [x] 1.4 Define which fields are safe to preserve and document excluded sensitive/volatile material.

## 2. Archive Command

- [x] 2.1 Implement a local readiness evidence history command under `scripts/ci/` or `scripts/demo/`.
- [x] 2.2 Add explicit CLI options for entry label, commit/version label, output history directory, release evidence JSON/Markdown paths, hosted readiness JSON/Markdown paths, and benchmark comparison JSON/Markdown paths.
- [x] 2.3 Copy only explicitly supplied artifacts into the selected history entry directory.
- [x] 2.4 Record omitted optional evidence families as `not_provided` rather than inferred pass.
- [x] 2.5 Validate missing or unreadable provided source paths with clear errors or non-clean entry status.
- [x] 2.6 Keep the command non-mutating except for writing the selected history files and index.

## 3. Index And Trend Summary

- [x] 3.1 Generate an `entry.json` summary for each archived evidence entry.
- [x] 3.2 Generate or update a deterministic `index.json` from archived entries.
- [x] 3.3 Generate an operator-readable Markdown index summary.
- [x] 3.4 Add an offline trend summary mode that compares recent entries for release status, hosted readiness status, benchmark movements, warnings, blockers, and operator-guided/not-provided counts.
- [x] 3.5 Ensure trend summaries preserve warning, blocking, operator-guided, known-limitation, and not-provided states.

## 4. Documentation

- [x] 4.1 Update release checklist with the readiness evidence history workflow.
- [x] 4.2 Update hosted preview readiness or hosted operator docs with how to archive hosted readiness artifacts.
- [x] 4.3 Update real-repository validation docs with how benchmark comparison evidence participates in readiness history.
- [x] 4.4 Document that `.tmp` remains scratch and durable history requires explicit archive command input.

## 5. Tests

- [x] 5.1 Add tests for entry summary extraction from release evidence, hosted readiness, and benchmark comparison JSON.
- [x] 5.2 Add tests for missing optional evidence families and invalid provided paths.
- [x] 5.3 Add tests for artifact copy behavior, deterministic index generation, and Markdown summary generation.
- [x] 5.4 Add tests for trend summary behavior across multiple evidence entries.
- [x] 5.5 Run targeted readiness evidence history tests.
- [x] 5.6 Run related release evidence, hosted readiness, and benchmark comparison tests.
- [x] 5.7 Run `openspec validate readiness-evidence-history --type change --strict`.
