# Self-Hosted Readiness Checklist

[Home](../../README.md) | [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) | [Deployment](deployment.md) | [Release Checklist](release-checklist.md) | [Hosted Preview Readiness](hosted-preview-readiness.md)

---

Use this checklist before claiming a local/private DecisionAtlas deployment is ready for customer evaluation, Team Self-hosted use, or Enterprise Self-hosted handoff.

## Boundary

This checklist validates the self-hosted product baseline. It does not validate:

- billing
- full SaaS organization management
- hosted multi-tenancy
- GitHub Marketplace or self-service OAuth installation
- hosted secret vault
- permanent buyout licensing
- managed hosted service operations

## Environment

- [ ] PostgreSQL is running and `DATABASE_URL` targets the intended database.
- [ ] Redis is running and `REDIS_URL` targets the intended Redis instance.
- [ ] Engine starts and exposes `http://localhost:8000/health` or the configured private URL.
- [ ] API starts and exposes `http://localhost:3001/health` or the configured private URL.
- [ ] Web starts and serves `http://localhost:3000` or the configured private URL.
- [ ] Browser-facing configuration does not contain provider API keys or repository credentials.
- [ ] Provider credentials, if used, are configured only on backend/customer-controlled host surfaces.
- [ ] Private repository access, if used, has a documented owner-scoped token or installation boundary.

## Startup And Product Flow

- [ ] `powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1` starts the real stack.
- [ ] `powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1` stops the managed local stack.
- [ ] `demo-workspace` is present.
- [ ] Review page shows at least one reviewable candidate when the guided demo lane is expected.
- [ ] Why-search returns cited output or an explicit bounded limitation.
- [ ] Drift page shows expected seeded or imported-workspace drift state.
- [ ] Repeat repository analysis explains open-existing, sync, and full rerun choices.

## Validation Commands

Run the canonical checks:

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

Record results:

- [ ] OpenSpec strict validation result recorded.
- [ ] Governance guardrail result recorded.
- [ ] Canonical pre-release result recorded.
- [ ] Any `caution` or `pause` guardrail evidence is disclosed.
- [ ] Any test failure is classified before customer handoff.

## Evidence Generation

Generate release evidence:

```powershell
python scripts\ci\collect_release_evidence.py `
  --pre-release-status passed `
  --openspec-status passed `
  --offline-benchmark-status passed `
  --guardrail-report .tmp/agent-guardrail.json `
  --benchmark-comparison-report .tmp/real-repo-benchmark-comparison.json
```

Generate hosted/operator readiness evidence:

```powershell
python scripts\demo\collect_hosted_readiness.py `
  --health-status operator_guided `
  --smoke-status operator_guided `
  --seeded-readiness-status pass `
  --recovery-status operator_guided `
  --release-evidence-report .tmp/release-evidence.json `
  --real-repo-evidence-report .tmp/real-repo-benchmark-comparison.json
```

Archive durable readiness evidence:

```powershell
python scripts\ci\collect_readiness_evidence_history.py archive `
  --label self-hosted-readiness `
  --release-evidence-json .tmp/release-evidence.json `
  --release-evidence-markdown .tmp/release-evidence.md `
  --hosted-readiness-json .tmp/hosted-operator-readiness.json `
  --hosted-readiness-markdown .tmp/hosted-operator-readiness.md `
  --benchmark-comparison-json .tmp/real-repo-benchmark-comparison.json `
  --benchmark-comparison-markdown .tmp/real-repo-benchmark-comparison.md
```

Review:

- [ ] `.tmp/release-evidence.json` and `.tmp/release-evidence.md` generated.
- [ ] `.tmp/hosted-operator-readiness.json` and `.tmp/hosted-operator-readiness.md` generated.
- [ ] Benchmark comparison JSON/Markdown generated or explicitly marked not provided.
- [ ] `docs/evidence/readiness/index.md` and `docs/evidence/readiness/trend.md` reviewed when evidence is archived.
- [ ] `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states are preserved.

## Backup, Recovery, And Upgrade

- [ ] PostgreSQL backup path is documented before customer evaluation.
- [ ] Redis recovery expectation is documented.
- [ ] `.env` and customer-controlled credentials are backed up outside source control.
- [ ] Seeded demo readiness check has been run:

```powershell
python scripts\demo\check_seeded_demo.py
```

- [ ] Reset command is known:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

- [ ] Reseed command is known:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

- [ ] Imported workspace cleanup is not implied by default seeded demo recovery.
- [ ] Upgrade rollback expectation is documented: restore prior app revision and database backup, then rerun readiness checks.

## Handoff Classification

Use these states in customer-facing handoff:

- `pass`: current evidence supports the lane.
- `warning`: usable but requires disclosure or follow-up.
- `blocking`: do not claim readiness until resolved or excluded.
- `operator_guided`: operator action, URL, credential, provider, or manual decision is still required.
- `known_limitation`: current environment cannot validate the lane; rerun command or condition is known.
- `not_provided`: optional evidence was omitted and must not be treated as pass.

## Minimum Customer Handoff

- [ ] Self-hosted tier boundary reviewed.
- [ ] Deferred SaaS capabilities disclosed.
- [ ] Deployment and validation commands recorded.
- [ ] Evidence bundle and readiness history attached or referenced.
- [ ] Code Decision Audit report prepared if this is a paid pilot.
- [ ] Limitations and recommended next actions are explicit.
