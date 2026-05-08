## Context
DecisionAtlas already has several release confidence sources: canonical pre-release checks, OpenSpec strict validation, governance protocol and guardrail summaries, deterministic benchmark validation, and optional real-repo benchmark comparison output. The gap is not that validation is absent; the gap is that release evidence is still manually collected and copied into checklists, PR notes, archives, or hosted-preview handoffs.

This change introduces a local evidence aggregation layer that makes release readiness easier to review without changing the meaning of existing gates.

## Goals / Non-Goals
### Goals
- Generate one local release evidence bundle with both machine-readable JSON and operator-readable Markdown output.
- Normalize canonical release gate results, OpenSpec validation, governance guardrail status, targeted test summaries, offline benchmark checks, and optional real-repo benchmark comparison reports.
- Keep mandatory release gates separate from advisory confidence signals.
- Make missing optional evidence visible instead of silently treating it as success.
- Preserve source paths, timestamps, command summaries, and advisory warnings so a reviewer can trace what was used.
- Keep the command deterministic and local by default.

### Non-Goals
- Do not create a hosted release dashboard.
- Do not add billing, tenancy, marketplace, or self-serve OAuth work.
- Do not make optional live repository benchmark failures block default CI unless an explicit future policy says so.
- Do not create git tags, push commits, publish releases, or mutate OpenSpec archives.
- Do not parse arbitrary human logs beyond bounded, documented inputs.

## Decisions
### Evidence Bundle Shape
The bundle should be generated as JSON plus Markdown. JSON is the source of truth for automation. Markdown is the human handoff for release notes, archive summaries, PR descriptions, and operator review.

The JSON should include:
- `generated_at`
- `schema_version`
- `overall_status`
- `required_gates`
- `advisory_signals`
- `evidence_items`
- `missing_inputs`
- `warnings`
- `source_paths`

### Mandatory and Advisory Separation
Canonical release validation remains the primary release gate. Governance warnings, `caution` states, and optional real-repo benchmark regressions should be disclosed clearly, but they should not be collapsed into the same boolean unless the operator explicitly opts into a stricter policy later.

### Explicit Inputs
The command should accept explicit report paths for optional evidence, especially real-repo benchmark comparison results. It should not scan broad temporary directories or silently reuse stale `.tmp` files.

### Local First
The default command should not require network access. Live repository benchmarks can still be run by existing benchmark commands before evidence generation; this change consumes those outputs rather than making release evidence generation responsible for network-heavy validation.

### Minimal Surface Area
Implementation should prefer a small script under `scripts/ci/` or `scripts/release/` and focused tests. No database, service API, or frontend product changes are expected.

## Risks / Trade-offs
- **Risk: stale evidence paths.** Mitigation: record exact source paths, generated timestamp, and missing-input warnings.
- **Risk: release overclaiming.** Mitigation: render required gates and advisory signals in separate sections and avoid treating `caution` as clean success.
- **Risk: brittle log parsing.** Mitigation: prefer JSON inputs where available and keep log parsing bounded to known command output formats.
- **Risk: slow release flow.** Mitigation: aggregate existing results by default; do not rerun live or expensive checks automatically.
- **Trade-off: local artifact over dashboard.** This is intentionally lower ceremony and more useful for the current repo maturity stage; dashboard/operator UI work can follow after evidence format stabilizes.
