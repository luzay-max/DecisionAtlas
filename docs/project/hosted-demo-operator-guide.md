# Hosted Demo Operator Guide

[Home](../README.md) | [Quick Start](quick-start.md) | [Deployment](deployment.md) | [Hosted Preview Readiness](hosted-preview-readiness.md) | [Demo Script](demo-script.md) | [中文](hosted-demo-operator-guide_zh-CN.md)

---

This guide is for operating a single-machine hosted DecisionAtlas demo. It is an operator runbook for a running environment, not a replacement for the default local release gate.

For external preview preparation, use [Hosted Preview Readiness](hosted-preview-readiness.md) as the concise pre-demo checklist and record results in `v0-3-hosted-preview-readiness-report.md`.

## Environment Contract

The hosted demo keeps the current topology:

```text
public traffic -> web -> api -> engine -> postgres / redis
```

Minimum hosted environment:

| Variable | Surface | Required | Notes |
|----------|---------|----------|-------|
| `DATABASE_URL` | engine | yes | PostgreSQL for hosted operation, SQLite only for isolated local demo stacks |
| `REDIS_URL` | engine | yes | Required for the real stack and import job coordination |
| `ENGINE_BASE_URL` | api | yes | Internal URL for the engine service |
| `API_BASE_URL` | web | yes | Browser-facing web build/runtime must reach the API through this URL |
| `DEMO_REPO` | engine | optional | Defaults to the curated demo repository used by the seeded lane |

Optional live-provider environment:

| Variable | Surface | Notes |
|----------|---------|-------|
| `LLM_PROVIDER_MODE` | engine | Use `openai_compatible` for live provider mode, `fake` for seeded/local smoke |
| `LLM_API_KEY` | engine | Backend-only secret |
| `LLM_MODEL` | engine | Live model name |
| `EMBEDDING_MODEL` | engine | Live embedding model name |
| `EMBEDDING_API_KEY` | engine | Optional backend-only secret if different from `LLM_API_KEY` |
| `LLM_BASE_URL` | engine | Optional compatible provider endpoint |
| `GITHUB_TOKEN` | engine | Optional backend-only token for public GitHub rate limits |
| `GITHUB_APP_WEBHOOK_SECRET` | engine | Optional backend-only secret used to verify GitHub App webhook signatures |

Provider keys and repository credentials must stay on host-managed or backend-only surfaces. Do not expose them through browser-visible config, client bundles, or public logs.

## Lane Boundary

The stable public walkthrough is the seeded workspace:

```text
demo-workspace
```

Imported real-repository workspaces are a separate operator-managed lane. They can be used as a bounded credibility check, but they are not the primary public walkthrough and are not reset by the default demo recovery scripts.

## GitHub App Webhook Sync Operations

GitHub App installation binding is an admin/operator setup flow. Full GitHub Marketplace/OAuth self-service installation is still out of scope, but an operator can validate webhook-driven incremental sync for an already installed GitHub App.

Webhook endpoint:

```text
POST /imports/github/webhook
```

Expected headers:

| Header | Required | Notes |
|--------|----------|-------|
| `X-GitHub-Event` | yes | Supported events: `push`, `pull_request`, `issues` |
| `X-GitHub-Delivery` | recommended | Used as delivery provenance for the queued sync |
| `X-Hub-Signature-256` | required when `GITHUB_APP_WEBHOOK_SECRET` is set | Must match the backend-only webhook secret |

Validation path:

1. Bind the repository to an installation from the admin GitHub App setup panel.
2. Confirm the workspace or lookup surface shows the GitHub App installation access-source label.
3. Send or replay a supported webhook event for the same installation and repository.
4. Confirm the workspace dashboard/readiness surface shows webhook-triggered sync provenance.
5. Keep the default release gate separate: live webhook delivery is operator-guided and is not required by `scripts/ci/pre-release.ps1`.

Troubleshooting:

- `missing installation binding`: bind the repository and installation before replaying the webhook.
- `unmatched repository`: confirm the webhook payload repository full name matches the bound imported workspace.
- `invalid headers or signature`: verify event headers and `GITHUB_APP_WEBHOOK_SECRET`; the secret must remain backend-only.
- `duplicate active sync`: wait for the current queued/running sync to finish before replaying the delivery.
- `provider or network failure`: inspect the latest import failure and rerun the same delivery after provider/network recovery.

Deferred scope:

- Full GitHub Marketplace/OAuth self-service setup.
- Hosted live webhook delivery as a default release-gate requirement.

## Private Repository Access Operations

Token-backed private repository access is an admin/operator setup flow for the current owner scope. It is intended for bounded hosted-preview validation and controlled real-repository checks, not for full SaaS secret management.

Recommended token boundary:

- Use a GitHub token with the minimum repository read access required for the target private repository.
- Prefer a token dedicated to the hosted preview environment rather than a personal day-to-day token.
- Treat submitted tokens as backend-only credentials. They must not appear in browser-visible config, client bundles, logs, screenshots, or shared reports.
- Rotate the token if repository permissions change, if access is revoked, or after a hosted-preview exercise that used sensitive data.

Validation path:

1. Sign in as an admin for the intended owner scope.
2. Open the private repository access setup panel.
3. Submit `owner/private-repo`, the token, and an operator-friendly source label.
4. Confirm the product result shows the private GitHub source label, authorization status, and workspace slug without echoing the submitted token.
5. Open the workspace dashboard or readiness surface and confirm the same access-source label and status are visible before import, sync, or review actions.

Troubleshooting:

- `missing source` or `credential_required`: create or rebind the private access source for the current owner scope.
- `unauthorized`, `authorization_failed`, or `invalid`: rotate the token or grant it read access to the repository, then bind again.
- `repository_not_found`: confirm the repository name and whether the token can see that private repository.
- `provider_failure` or `network_failure`: retry after GitHub or network recovery; do not rotate credentials unless the failure persists as authorization-specific.
- `stale status`: rebind or rerun a validation import so the access-source status reflects current GitHub permissions.

Deferred scope:

- No secret vault or encrypted credential-management UI.
- No token rotation history or credential audit-log UI.
- No GitHub OAuth / Marketplace self-service private repository onboarding.
- No live private repository credentials in default CI or `scripts/ci/pre-release.ps1`.

## Health Check

Run this against a running hosted environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

For the local managed demo stack:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
```

The check verifies the web surface, API health, engine health, and dependency reachability when `DATABASE_URL` or `REDIS_URL` are available in the operator shell.

## Smoke Check

Run this after health checks pass:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1 `
  -WebBaseUrl "https://your-demo.example.com" `
  -ApiBaseUrl "https://your-api.example.com" `
  -EngineBaseUrl "https://your-engine.example.com"
```

This runs the guided demo Playwright smoke against the already running web URL. It sets `PLAYWRIGHT_SKIP_WEBSERVER=1`, so Playwright does not start local services.

## Reset Versus Reseed

Use reset when the seeded demo workspace has drifted because of demo interaction, review state, or temporary data changes:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

Use reseed when migrations may be out of date or the hosted database needs a deeper demo baseline rebuild:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

Both scripts require `DATABASE_URL` in the operator shell. For the local isolated demo stack, pass `-UseLocalDemoDatabase`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

Default reset and reseed actions target only `demo-workspace`. Imported workspaces are not deleted unless a future operator script explicitly says so.

## Operator Checklist

Before a public demo:

- Review [Hosted Preview Readiness](hosted-preview-readiness.md) and confirm there are no `blocking` items in the current readiness report.
- Confirm backend-only secrets are set only on host/backend surfaces.
- Run hosted health check.
- Run hosted smoke check.
- Open `/workspaces/demo-workspace`.
- Keep imported real-repo proof optional and separate from the main walkthrough.

If the walkthrough state looks wrong:

- Run `reset-demo.ps1` first.
- Run `reseed-demo.ps1` if reset does not recover the expected baseline.
- Re-run health and smoke checks.

## Relationship To Release Validation

The hosted checks are operator-guided validation for a running environment. The default branch/release gate remains:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

## Validated Local Operator Path

Last validated: 2026-04-24

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase
```

This path validates the operator commands against the isolated local demo stack. Hosted environments should pass explicit `-WebBaseUrl`, `-ApiBaseUrl`, and `-EngineBaseUrl` values.
