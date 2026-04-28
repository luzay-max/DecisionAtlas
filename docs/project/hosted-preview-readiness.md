# Hosted Preview Readiness

[Home](../README.md) | [Quick Start](quick-start.md) | [Deployment](deployment.md) | [Hosted Operator Guide](hosted-demo-operator-guide.md) | [Demo Script](demo-script.md) | [中文](hosted-preview-readiness_zh-CN.md)

---

This checklist prepares DecisionAtlas v0.3 RC for an externally hosted preview. It is a post-RC confidence layer for a running environment, not a replacement for the canonical local release gate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

## Preview Boundary

The hosted preview is not a production SaaS release. It does not include SLA, billing, full organization management, a secret vault, GitHub Marketplace/OAuth self-service installation, multiplayer review, or unlimited public repository import.

The stable public walkthrough is the seeded guided demo lane:

```text
demo-workspace
```

Imported real-repository workspaces, GitHub App sync, and token-backed private repository access are optional operator/admin demonstrations. They depend on provider, credential, GitHub, and network state and should not be required to complete the public walkthrough.

## Minimum Environment Conditions

| Area | Required preview condition | Status values |
| --- | --- | --- |
| Web | Public URL serves the Next.js app | pass / blocking / known limitation |
| API | API health endpoint is reachable from web and operator shell | pass / blocking / known limitation |
| Engine | Engine health endpoint is reachable from API and operator shell | pass / blocking / known limitation |
| Database | Hosted `DATABASE_URL` points to the intended PostgreSQL instance | pass / blocking / known limitation |
| Redis | Hosted `REDIS_URL` points to the intended Redis instance | pass / blocking / known limitation |
| Seeded demo data | `demo-workspace` is present and walkthrough-ready | pass / blocking / known limitation |
| Recovery | Reset or reseed path is known and rehearsed when possible | pass / non-blocking / known limitation |
| Secrets | Provider keys and repository credentials stay backend-only | pass / blocking |
| Imported lane | Optional real-repo workspace state is understood before showing it | pass / non-blocking / known limitation |

## Required Operator Checks

Run health against the externally hosted services:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

Run the hosted guided-demo smoke check:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

If the hosted environment is unavailable during local preparation, record the check as `operator-guided / unavailable` in the readiness report rather than treating it as passed.

## Recovery Drill

Use reset for a drifted seeded walkthrough state:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

Use reseed when migrations or deeper data drift require rebuilding the seeded baseline:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

For local rehearsal against the isolated demo database:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

Default reset and reseed actions target only `demo-workspace`. They must not be described as imported-workspace cleanup.

## External Walkthrough

1. Open the home page and state the boundary: the guided demo is stable seeded data; advanced/imported lanes are optional.
2. Open `/workspaces/demo-workspace`.
3. Confirm the dashboard recommends the next walkthrough step.
4. Open `/review?workspace=demo-workspace` and explain human review.
5. Open `/search?workspace=demo-workspace` and ask `why use redis cache`.
6. Open `/timeline?workspace=demo-workspace` and show accepted decisions as durable memory.
7. Open `/drift?workspace=demo-workspace` and explain conservative drift.
8. Optional: show imported workspace readiness or admin access-source panels only after explaining provider/credential/network dependency.

## Pass / Fail Classification

- `pass`: the hosted environment or local rehearsal produced the expected result.
- `blocking`: the public walkthrough cannot be shown reliably until fixed.
- `non-blocking`: the public walkthrough still works, but an optional lane or operator detail needs follow-up.
- `known limitation`: the check depends on unavailable hosted infrastructure, credentials, providers, GitHub, or network state and has a clear rerun command.

## Pre-Demo Minimum

Before an external walkthrough, the operator should have:

- health check result for web/API/engine.
- smoke check result for the seeded guided demo.
- reset/reseed command known and preferably rehearsed.
- current readiness report reviewed for blockers.
- imported and private lanes either validated or explicitly excluded from the public walkthrough.
