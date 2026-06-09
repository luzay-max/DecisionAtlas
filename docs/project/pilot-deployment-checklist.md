# Pilot Deployment Checklist

[Pilot Kit](pilot-customer-delivery-kit.md) | [Package Guide](self-hosted-package-guide.md) | [Operations Runbook](self-hosted-operations-runbook.md)

---

Use this checklist before a self-hosted pilot starts.

## 1. Scope

- [ ] Identify pilot owner and operator.
- [ ] Identify target repository or repositories.
- [ ] Decide public, private token, installation, or operator-guided access path.
- [ ] Confirm whether model provider credentials are available.
- [ ] Confirm whether the pilot is Community, Team Self-hosted, or Enterprise Self-hosted.

## 2. Environment

- [ ] Prepare PostgreSQL.
- [ ] Prepare Redis.
- [ ] Install Node.js, `pnpm`, Python, and `uv`.
- [ ] Copy `templates/self-hosted.env.example` to `.env`.
- [ ] Configure `DATABASE_URL`, `REDIS_URL`, `ENGINE_BASE_URL`, `API_BASE_URL`, and bootstrap settings.
- [ ] Keep provider keys, repository tokens, `.env`, database dumps, and private repository contents outside source control.

## 3. Startup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.bat
```

Verify:

- [ ] Web opens at `http://127.0.0.1:3000`.
- [ ] API health returns pass.
- [ ] Engine health returns pass.
- [ ] First admin can initialize or recover bootstrap access.

## 4. Repository Import

- [ ] Configure repository access through admin/operator flow.
- [ ] Confirm access mode and provider boundary.
- [ ] Import or reuse workspace.
- [ ] Confirm candidate decisions are visible.
- [ ] Record import outcome, blocker, or operator-guided condition.

## 5. Team Workflow

- [ ] Create or confirm admin user.
- [ ] Create reviewer account.
- [ ] Create viewer account.
- [ ] Confirm reviewer can review decisions and drift.
- [ ] Confirm viewer can read but cannot mutate.
- [ ] Preserve review and drift audit history.

## 6. Evidence

Generate or attach:

- [ ] package verification
- [ ] release evidence
- [ ] hosted/operator readiness
- [ ] benchmark comparison or explicit `not_provided`
- [ ] clean install rehearsal
- [ ] readiness evidence history entry
- [ ] team handoff report
- [ ] license/support boundary and entitlement record when applicable

## 7. Pilot Closeout

- [ ] Review accepted/rejected decisions.
- [ ] Review why-search examples.
- [ ] Review drift outcomes.
- [ ] Record limitations and non-pass evidence states.
- [ ] Decide whether to extend, convert to Team Self-hosted, scope Enterprise support, or stop.
