## Why

DecisionAtlas now has deterministic tests, OpenSpec validation, advisory guardrails, and real-repo benchmark comparison output, but release evidence is still manually copied into checklists and handoffs. This change creates a local release evidence bundle so maintainers can generate one structured summary of what passed, what is advisory, and what still needs human disclosure before release or preview claims.

## What Changes

- Add a local release evidence command that aggregates known validation outputs into one machine-readable and operator-readable bundle.
- Capture canonical release gate status, OpenSpec strict validation status, governance protocol/guardrail status, targeted test summaries, offline benchmark validation, and optional real-repo benchmark comparison evidence.
- Preserve advisory boundaries: `caution` and optional live benchmark blockers are disclosed, not silently treated as default CI failures.
- Generate a Markdown handoff suitable for release notes, archive handoff, PR summary, or hosted-preview readiness notes.
- Keep the command local and deterministic by default; optional live/benchmark comparison inputs must be explicit file paths.
- Do not implement billing, hosted dashboards, SaaS release management, or default CI enforcement.

## Capabilities

### New Capabilities

- `release-evidence-automation`: local release evidence aggregation, validation summary normalization, machine-readable output, and Markdown handoff generation.

### Modified Capabilities

- `release-baseline-validation`: clarify that release evidence bundles can summarize canonical release validation plus advisory confidence layers without replacing the canonical release gate.

## Impact

- New or extended local script under `scripts/ci/` or `scripts/release/` for collecting release evidence.
- Optional use of existing commands: `openspec validate --all --strict`, `scripts/ci/pre-release.ps1`, `scripts/governance/agent_guardrail.py --protocol-status --summary`, `scripts/ci/run_benchmark.py`, and real-repo benchmark comparison report paths.
- Tests for evidence parsing, missing-input handling, advisory status classification, and Markdown output.
- Docs update in `docs/project/release-checklist.md` or adjacent release docs.
- No database migration and no runtime product API changes expected.
