## 1. Candidate Promotion Script

- [x] 1.1 Add a dry-run-first script to inspect candidate and accepted decisions.
- [x] 1.2 Add explicit confirmed accept mode with bounded `--max-accept` and required rationale.
- [x] 1.3 Emit JSON and Markdown evidence with before/after baseline counts.

## 2. Tests

- [x] 2.1 Add unit tests for dry-run mode.
- [x] 2.2 Add unit tests for confirmed accept mode and API failure handling.
- [x] 2.3 Run targeted tests and `openspec validate --all --strict`.

## 3. Real Rehearsal

- [x] 3.1 Run dry-run rehearsal against the real `rich` imported workspace.
- [x] 3.2 Run confirmed bounded accept against the real local stack if candidate decisions are available.
- [x] 3.3 Regenerate baseline evidence and browser validation.

## 4. Records

- [x] 4.1 Archive readiness evidence and update project logs/taskbook.
- [x] 4.2 Archive the OpenSpec change and commit.
