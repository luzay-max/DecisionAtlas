# 2026-05-06 Update Log

## Summary

- Completed stage 7: AI Agent Governance Integration.
- Added a local AI-agent governance guardrail that aggregates current-diff governance checks and long-term drift detection into `continue` / `caution` / `pause`.
- Synced and archived the OpenSpec change `integrate-ai-agent-governance-guardrails`.
- Fixed a real-stack startup blocker caused by an Alembic revision ID exceeding Postgres' default Alembic version table length.
- Re-ran the real-stack full-chain browser check against the user-started project.

## 2026-05-08 Full-Chain Governance Interface Update

- Added the AI-agent governance guardrail interface to the canonical release gate in `scripts/ci/pre-release.ps1`.
- Recorded the interface availability check in `docs/project/release-checklist.md`.
- Committed the gate update as `bb5753a test: include governance guardrail in release gate`.
- Re-validated the guardrail on a clean working tree:
  - `python scripts/governance/agent_guardrail.py --summary` -> `continue`
  - `python scripts/governance/agent_guardrail.py --enforcement-preview release-checklist --summary` -> `pass`, `would_block=false`
  - `python scripts/governance/drift_report.py --pretty` -> `clean`
- Re-ran the canonical full-chain gate after the commit:
  - OpenSpec strict validation: passed
  - workspace tests/typecheck: passed
  - engine pytest: `216 passed`
  - offline benchmark fixture validation: passed
  - AI-agent governance guardrail interface availability: passed
  - Playwright smoke: `1 passed`
- Re-validated the real stack:
  - `start-real-stack.ps1 -ResetSeededDemo` succeeded
  - seeded demo ready: `accepted=4, candidate=1, source_refs=8, timeline=4, open_drift_alerts=1`
  - hosted smoke passed
  - live real-repo benchmark for `browser-use/browser-use` passed with `why_ready` / `useful_now`

## Completed Work

### Stage 7 AI agent governance guardrail

- Added `services/engine/app/governance/agent_guardrail.py`.
- Added `scripts/governance/agent_guardrail.py` as the local agent-facing entrypoint.
- Added `docs/project/governance-agent-guardrail.md`.
- Added `services/engine/tests/governance/test_agent_guardrail.py`.
- Added the main OpenSpec capability at `openspec/specs/ai-agent-governance-guardrails/spec.md`.
- Archived the change at `openspec/changes/archive/2026-05-06-integrate-ai-agent-governance-guardrails/`.

The guardrail intentionally remains advisory:

- `continue`: no blocking or caution-level governance concern detected.
- `caution`: advisory concerns exist; address recommended actions before claiming completion.
- `pause`: human review is required before the agent continues.

It does not automatically edit code, update specs, rewrite governance rules, or block CI.

### Real-stack migration fix

- Fixed `services/engine/alembic/versions/0008_add_governance_markdown_ingest.py`.
- Renamed the revision ID from `0008_add_governance_markdown_ingest` to `0008_governance_ingest`.
- Added `services/engine/tests/db/test_migrations.py` to enforce Alembic revision IDs fit the default `alembic_version.version_num varchar(32)` limit.

Root cause:

```text
0008_add_governance_markdown_ingest is 35 characters.
Alembic's default version_num column is varchar(32).
Postgres rejected the version update during migration.
```

### Real-stack full-chain check

The running real stack was checked after the migration fix:

- Engine health: `http://127.0.0.1:8000/health` returned `{"ok":true}`.
- API health: `http://127.0.0.1:3001/health` returned `{"ok":true}`.
- Web home: `http://127.0.0.1:3000` returned `200`.
- Playwright demo smoke passed.
- Browser console errors: none observed.
- Engine/API/Web stderr logs: no runtime errors observed during the check.

Checked product surfaces:

- Home page and language toggle.
- Guided demo entry.
- Demo workspace dashboard.
- Review page.
- Why search demo question and manual Redis query.
- Timeline page and decision detail navigation.
- Drift page and decision detail navigation.
- Governance Markdown import form.
- Advanced real repository analysis form button enablement.

## Validation

Commands run:

```text
python -m pytest services/engine/tests/governance/test_agent_guardrail.py -q
python -m pytest services/engine/tests/governance/test_diff_checker.py services/engine/tests/governance/test_drift_detector.py services/engine/tests/governance/test_agent_guardrail.py -q
python scripts/governance/agent_guardrail.py --summary
openspec validate integrate-ai-agent-governance-guardrails --type change --strict
openspec validate --all --strict
services/engine/.venv/Scripts/python.exe -m pytest tests/db/test_migrations.py tests/db/test_schema.py -q
services/engine/.venv/Scripts/alembic.exe upgrade head
scripts/dev/start-real-stack.bat
pnpm --filter @decisionatlas/web exec playwright test
```

Observed results:

- Governance guardrail tests: `6 passed`.
- Governance stage 5/6/7 tests: `19 passed`.
- OpenSpec all strict validation: passed.
- Migration tests from `services/engine`: `2 passed`.
- Postgres `alembic upgrade head`: passed.
- `scripts/dev/start-real-stack.bat`: exit code `0`.
- Playwright smoke: `1 passed`.

Note:

- `uv` was not available in the current shell, so Python validation used the project venv where needed.

## Current State

- OpenSpec active changes: `0`.
- Stage 7 is implemented and archived.
- The latest committed baseline is `bb5753a test: include governance guardrail in release gate`.
- Local `main` remains ahead of `origin/main` by 5 committed changes.
- The only untracked file in the working tree is `codex-history-repair.skill`, which remains intentionally ignored.

## Follow-Up

- Push the committed gate update when network/policy allows.
- Keep the new AI-agent governance guardrail interface in the canonical release gate and summary docs.
- Continue with the stage 8 governance workflow hardening and demo reset reliability route already laid out in the master plan.
