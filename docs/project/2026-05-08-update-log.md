# 2026-05-08 Update Log

## Summary

- Formalized the default local governance development protocol for AI-assisted and developer-driven changes.
- Added governance rule lifecycle review support for stale and superseded accepted rules.
- Turned real-repository benchmark evidence into repeatable snapshot and comparison output.
- Added release evidence automation so release validation, guardrail, benchmark, and advisory signals can be bundled into JSON and Markdown handoff artifacts.
- Added hosted/operator delivery readiness automation so external preview preparation can produce lane-based JSON and Markdown readiness evidence.

## Completed Changes

### Default governance development protocol

- Archived OpenSpec change: `2026-05-08-default-governance-development-protocol`.
- Added `python scripts/governance/agent_guardrail.py --protocol-status --summary` as the default preflight/postflight/archive/commit governance checkpoint.
- Updated README, Chinese README, guardrail docs, and AI-agent governance specs.
- Kept the protocol advisory by default and separate from canonical release validation and optional enforcement preview.

### Governance rule lifecycle review

- Archived OpenSpec change: `2026-05-08-add-governance-rule-lifecycle-review`.
- Added lifecycle metadata for accepted governance rules, including rationale and supersession traceability.
- Added API and UI support for updating rule lifecycle status.
- Updated diff/drift/markdown ingest behavior so inactive accepted rules can be disclosed with source evidence instead of silently disappearing.

### Real-repository benchmark regression evidence

- Archived OpenSpec change: `2026-05-08-real-repo-benchmark-regression`.
- Added compact real-repo benchmark history snapshots.
- Added current-vs-baseline benchmark comparison output with movement classification.
- Added Markdown comparison reports for release and operator handoff.
- Updated real-repository validation docs and specs.

### Release evidence automation

- Archived OpenSpec change: `2026-05-08-release-evidence-automation`.
- Added `python scripts/ci/collect_release_evidence.py`.
- Generated release evidence as machine-readable JSON and operator-readable Markdown.
- Preserved separation between required gates and advisory signals.
- Updated release checklist and release evidence specs.

### Hosted/operator delivery readiness

- Archived OpenSpec change: `2026-05-08-hosted-operator-delivery-readiness`.
- Added `python scripts/demo/collect_hosted_readiness.py`.
- Generated hosted readiness evidence as machine-readable JSON and operator-readable Markdown.
- Added lane-based classifications: `pass`, `blocking`, `non_blocking`, `known_limitation`, `operator_guided`, and `not_provided`.
- Ensured missing hosted URLs are recorded as `operator_guided`, not hidden as pass.
- Updated hosted operator guide and hosted preview readiness docs with stop/go rules, local rehearsal examples, and recovery evidence requirements.

## Validation

Commands run during the final hosted/operator readiness implementation:

```text
python -m pytest -q tests/ci/test_hosted_readiness.py
python -m pytest -q tests/ci/test_hosted_readiness.py tests/ci/test_release_evidence.py tests/test_hosted_demo_operator_flow.py
python -m pytest -q tests/test_seeded_demo_recovery.py
openspec validate hosted-operator-delivery-readiness --type change --strict
python scripts/demo/collect_hosted_readiness.py --generated-at 2026-05-08T00:00:00+00:00 --health-status operator_guided --smoke-status operator_guided --seeded-readiness-status pass --recovery-status operator_guided --output .tmp/hosted-readiness-smoke.json --markdown-output .tmp/hosted-readiness-smoke.md
```

Observed results:

- Hosted readiness tests: `4 passed`.
- Hosted readiness + release evidence + hosted operator flow tests: `12 passed`.
- Seeded demo recovery tests: `2 passed`.
- OpenSpec hosted/operator readiness strict validation: passed.
- Hosted readiness smoke run generated JSON/Markdown and returned `operator_guided` when hosted URLs were not supplied.

Environment note:

- The current shell did not have `uv`.
- The global Python environment was missing `alembic`; installing `alembic>=1.16.5` from official PyPI allowed seeded recovery tests to run.

## Current State

- OpenSpec active change `hosted-operator-delivery-readiness` has been implemented, validated, and archived.
- Main specs now include `hosted-operator-delivery-readiness`.
- Hosted/operator readiness is still local and non-mutating by default; it does not reset, reseed, import, run live benchmark checks, tag, push, publish, or replace `scripts/ci/pre-release.ps1`.
- The unrelated untracked file `codex-history-repair.skill` remains intentionally uncommitted.

## Follow-Up

- Push the accumulated local commits when ready.
- Use hosted readiness artifacts before any external preview.
- Next likely optimization lane: preserve readiness/benchmark evidence history across releases, then revisit hosted/operator recovery drills against real hosted URLs.
