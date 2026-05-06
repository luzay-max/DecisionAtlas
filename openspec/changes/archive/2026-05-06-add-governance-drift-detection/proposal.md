## Why

DecisionAtlas can now ingest accepted governance rules and check the current git diff, but it still lacks a way to detect whether the project is gradually drifting away from human-approved direction over time. Stage 6 should add a conservative governance drift report so roadmap, specs, accepted rules, archived changes, update logs, and repeated postmortem issues can be compared before drift becomes hidden product debt.

## What Changes

- Add a governance drift detection capability that produces a report over longer-lived project governance signals rather than only the current diff.
- Compare bounded evidence from roadmap and plan documents, main OpenSpec specs, archived OpenSpec changes, accepted governance rules, recent update logs, postmortem-style documents, and optionally the current workspace diff.
- Detect drift signals such as roadmap mismatch, spec gaps, stale or superseded rule usage, repeated historical issues, and human decisions that appear not to have been synchronized into specs or accepted governance rules.
- Return a structured advisory result with status, evidence-linked signals, human decision points, recommended next actions, and machine-readable output for future AI agent use.
- Keep the first version report-only and advisory: no CI blocking, no automatic code changes, no automatic rule rewrites, and no automatic promotion of inferred decisions to accepted rules.

## Capabilities

### New Capabilities

- `governance-drift-detection`: Detect long-term governance drift across roadmap, specs, archived changes, accepted rules, update logs, postmortems, and optional current diff context.

### Modified Capabilities

- None.

## Impact

- New governance drift detection module or script, likely adjacent to the existing governance diff checker.
- New structured report schema and tests with deterministic fixtures for clean, warning, and drift-detected cases.
- Documentation describing report status, signal types, evidence references, and advisory-only interpretation.
- No database migration or UI is required for the first usable local report unless implementation discovers that persistence is necessary.
