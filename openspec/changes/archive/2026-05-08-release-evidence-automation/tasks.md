## 1. Evidence Source Review

- [x] 1.1 Review current release checklist, pre-release script output, OpenSpec validation output, guardrail output, benchmark output, and real-repo benchmark comparison artifacts.
- [x] 1.2 Define the initial supported evidence input set and mark each input as required or optional.
- [x] 1.3 Confirm the command location and output directory convention for generated release evidence artifacts.

## 2. Evidence Model

- [x] 2.1 Add a small release evidence data model with schema version, generation metadata, required gates, advisory signals, missing inputs, warnings, source paths, and overall status.
- [x] 2.2 Implement status normalization for `passed`, `failed`, `warning`, `caution`, `missing`, and `not_provided` style inputs.
- [x] 2.3 Implement overall status calculation that keeps required gate failures separate from advisory cautions and optional benchmark blockers.
- [x] 2.4 Ensure every evidence item records its source path, command label, or explicit reason when source data is unavailable.

## 3. Collector CLI

- [x] 3.1 Implement a local release evidence command under `scripts/ci/` or `scripts/release/`.
- [x] 3.2 Add explicit CLI options for optional report paths, including guardrail output, benchmark comparison output, targeted test summary output, and canonical validation evidence.
- [x] 3.3 Prevent broad implicit temporary-file discovery and avoid silently reusing stale `.tmp` files.
- [x] 3.4 Handle missing optional inputs as disclosed missing evidence rather than clean success.
- [x] 3.5 Handle invalid required or provided source paths with clear warnings or non-clean status.

## 4. Output Generation

- [x] 4.1 Write the normalized evidence bundle as JSON.
- [x] 4.2 Generate a Markdown handoff that mirrors JSON statuses for required gates, advisory signals, benchmark evidence, missing inputs, warnings, and source paths.
- [x] 4.3 Include enough generated metadata in both outputs for a reviewer to trace when and from what inputs the bundle was created.
- [x] 4.4 Keep evidence generation local and non-mutating: no tags, pushes, archives, release publishing, or default network calls.

## 5. Documentation

- [x] 5.1 Update release checklist or adjacent release documentation to show how to generate and attach a release evidence bundle.
- [x] 5.2 Document which evidence inputs are required, which are optional, and how advisory statuses should be interpreted.
- [x] 5.3 Add an example release evidence command for a normal local release review and an example that includes real-repo benchmark comparison evidence.

## 6. Tests and Validation

- [x] 6.1 Add unit tests for evidence model normalization and overall status calculation.
- [x] 6.2 Add tests for missing optional input handling and invalid provided path handling.
- [x] 6.3 Add tests that Markdown output does not hide warnings, missing inputs, advisory cautions, or optional benchmark blockers.
- [x] 6.4 Run the targeted release evidence tests.
- [x] 6.5 Run relevant governance or release validation tests affected by this change.
- [x] 6.6 Run `openspec validate release-evidence-automation --type change --strict`.
