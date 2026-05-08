## 1. Readiness Checklist And Reports

- [x] 1.1 Audit hosted preview, hosted operator, release checklist, quick start, demo script, and governance guardrail docs for governed preview gaps.
- [x] 1.2 Update hosted preview readiness guidance with governed readiness lanes, status classification, guardrail smoke, governance Markdown ingest smoke, and optional real-repo value report evidence.
- [x] 1.3 Update or create the governed hosted preview readiness report with current commit state, unavailable hosted URL assumptions, validation commands, guardrail status handling, known limitations, and follow-ups.
- [x] 1.4 Ensure generated `.tmp/` live benchmark reports are documented as optional attach-or-summarize evidence rather than committed artifacts.

## 2. Governed External Walkthrough

- [x] 2.1 Update the external demo script so the first act remains `demo-workspace` dashboard, review, why-search, timeline, and drift.
- [x] 2.2 Add a bounded governance second act covering Markdown governance ingest, pending rule drafts, human acceptance, accepted-rule source evidence, and agent guardrail summary.
- [x] 2.3 Document how to explain guardrail `continue`, `caution`, and `pause` during preview without implying automatic enforcement.
- [x] 2.4 Preserve production non-goals in preview-facing docs: no billing, full org admin, secret vault, marketplace self-service, multiplayer review, or default CI enforcement.

## 3. Operator Runbook And Script Coverage

- [x] 3.1 Update hosted operator guidance with governed pre-demo order: health, smoke, seeded readiness, recovery, governance smoke, guardrail summary, optional real-repo report.
- [x] 3.2 Confirm existing demo recovery commands remain scoped to `demo-workspace` and documented as preserving imported workspaces and governance history.
- [x] 3.3 Add or update lightweight script/test coverage only if audit reveals a command or output gap for governed preview readiness.
- [x] 3.4 Keep all hosted and governance checks advisory/operator-guided and outside default `scripts/ci/pre-release.ps1`.

## 4. OpenSpec And Release Boundary Sync

- [x] 4.1 Sync governed hosted preview requirements across hosted-demo operator flow, guided demo, governance ingest, agent guardrail, real-repo benchmark, and release validation docs.
- [x] 4.2 Ensure release-facing docs continue to identify canonical local pre-release validation as the mandatory deterministic gate.
- [x] 4.3 Ensure governed preview docs state external hosted URL checks are `operator-guided` or `known limitation` when no hosted environment is supplied.

## 5. Validation

- [x] 5.1 Run targeted documentation/script tests affected by governed preview readiness changes.
- [x] 5.2 Run hosted/demo/governance smoke commands that are available locally and record unavailable hosted checks as operator-guided rather than passed.
- [x] 5.3 Run OpenSpec validation for `prepare-governed-hosted-preview`.
- [x] 5.4 Run the local agent governance guardrail and record any `caution` or `pause` evidence before archive.
