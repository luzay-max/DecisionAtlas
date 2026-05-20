# Self-Hosted Commercial Baseline

[Home](../../README.md) | [Quick Start](quick-start.md) | [Deployment](deployment.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Delivery Rehearsal](self-hosted-delivery-rehearsal.md) | [Code Decision Audit Template](code-decision-audit-template.md)

---

DecisionAtlas is currently packaged as a self-hosted / private-deployable decision-governance product. The near-term commercial path is not full hosted SaaS and not permanent buyout licensing. The supported direction is:

```text
Community
  local evaluation and public-repo proof
        │
        ▼
Team Self-hosted
  private repo, evidence history, team-ready handoff
        │
        ▼
Enterprise Self-hosted
  private deployment, operator support, security boundary docs
        │
        ▼
Future optional
  hosted managed service, billing, Marketplace/OAuth, SaaS admin
```

## Product Tiers

| Area | Community | Team Self-hosted | Enterprise Self-hosted |
| --- | --- | --- | --- |
| Intended use | Local evaluation, demo, public-repo validation | Small team private deployment | Enterprise private or offline deployment |
| Deployment | Local machine / Docker-backed real stack | Customer-managed self-hosted stack | Customer-managed private network or assisted deployment |
| Repository access | Public repos and demo data | Private repos through supported operator/admin setup | Private repos with customer-controlled credentials and deployment review |
| Workspaces | Demo and bounded evaluation workspaces | Multiple workspaces within the current owner-scope model | Multiple workspaces plus enterprise deployment conventions |
| Governance | Local governance reports and guardrail | Governance rule lifecycle and evidence handoff | Governance handoff, support workflow, and enterprise reporting conventions |
| Evidence | Manual release/readiness evidence | Release evidence history and benchmark trend evidence | Evidence history plus deployment/support handoff |
| Support | Community/self-guided | Paid support boundary | Assisted deployment, recovery guidance, and custom support scope |
| Runtime license enforcement | Not required by this baseline | Not required by this baseline | Not required by this baseline |

The tier boundaries are product and support packaging boundaries. This baseline does not add runtime license checks.

## Deferred Capabilities

The self-hosted baseline does not include:

- billing
- full SaaS organization management
- hosted multi-tenancy
- GitHub Marketplace or self-service OAuth installation
- hosted secret vault
- hosted credential custody
- permanent buyout license workflow
- multi-user collaborative review workflow beyond the current role-gated product actions
- managed hosted service operations

These are future optional hosted managed service work, not prerequisites for the current self-hosted product.

## Self-Hosted Setup Path

### Prerequisites

- Node.js and `pnpm`
- Python 3.11+ and `uv` or `python -m uv`
- Docker Desktop for PostgreSQL and Redis
- Optional `pandoc` for `.docx` import
- Optional OpenAI-compatible provider credentials for live provider mode
- Optional GitHub credentials for private repository operator/admin flows

### Install

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
```

### Configure Required Services

The self-hosted real stack uses:

- Web: `http://localhost:3000`
- API: `http://localhost:3001`
- Engine: `http://localhost:8000`
- PostgreSQL with pgvector
- Redis

Minimum environment variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ENGINE_BASE_URL` | Engine service URL used by API/web flows |
| `API_BASE_URL` | API service URL used by web/operator flows |
| `AUTO_BOOTSTRAP_AUTH` | Enables local/bootstrap session recovery in supported local/private deployments |

Live provider mode:

| Variable | Purpose |
| --- | --- |
| `LLM_PROVIDER_MODE` | Set to `openai_compatible` for live provider-backed import/search |
| `LLM_API_KEY` | Backend-only model provider key |
| `LLM_MODEL` | Chat/model identifier |
| `EMBEDDING_MODEL` | Embedding model identifier |
| `EMBEDDING_API_KEY` | Optional separate embedding key |
| `LLM_BASE_URL` | Optional OpenAI-compatible endpoint |

Provider keys and repository credentials must stay on backend or customer-controlled host surfaces. They must not be exposed to browser-facing configuration. This baseline does not include a hosted secret vault.

### Start And Stop

Start the full local/private stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

If the seeded demo lane was consumed before startup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1 -ResetSeededDemo
```

Stop the stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

Use the isolated demo stack only for local evaluation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

## Private Repository Boundary

Private repository access is an operator/admin setup flow. It is not a hosted credential-custody service.

Recommended minimum approach:

- Use the least-privileged token or installation path that can read the target repository.
- Bind access to the current owner scope rather than treating credentials as global.
- Validate repository lookup before starting a live import.
- Rotate or revoke credentials in the customer's environment when access fails or a token is no longer needed.
- Do not commit tokens, provider keys, raw private repository content, or generated `.tmp` reports that contain sensitive details.

Troubleshooting categories:

- missing credential or installation source
- unauthorized or revoked credential
- insufficient repository permission
- repository not found or not reachable
- provider/network failure
- stale workspace or active import/sync state
- model provider unavailable or misconfigured

## Validation And Evidence

Use [Self-Hosted Readiness Checklist](self-hosted-readiness-checklist.md) before claiming a self-hosted deployment is ready.

Use [Self-Hosted Delivery Rehearsal](self-hosted-delivery-rehearsal.md) before customer evaluation, paid pilot handoff, or enterprise delivery claims. Customer-facing readiness claims should reference a completed readiness history entry or explicitly disclose why rehearsal evidence is missing.

Core checks:

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

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
  --label self-hosted-evaluation `
  --release-evidence-json .tmp/release-evidence.json `
  --release-evidence-markdown .tmp/release-evidence.md `
  --hosted-readiness-json .tmp/hosted-operator-readiness.json `
  --hosted-readiness-markdown .tmp/hosted-operator-readiness.md `
  --benchmark-comparison-json .tmp/real-repo-benchmark-comparison.json `
  --benchmark-comparison-markdown .tmp/real-repo-benchmark-comparison.md
```

Evidence states such as `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` must be disclosed. Do not convert them into pass.

## Backup, Restore, Upgrade, And Recovery

Minimum operator expectations:

- Back up PostgreSQL before upgrading or running destructive maintenance.
- Preserve `.env` and customer-controlled secret/config sources outside source control.
- Keep generated `.tmp` output as scratch only unless explicitly archived through readiness evidence history.
- Use seeded reset for consumed demo state.
- Use reseed when migrations or data drift require rebuilding the seeded baseline.
- Treat imported workspaces separately from the seeded `demo-workspace` recovery lane.

Recovery commands:

```powershell
python scripts\demo\check_seeded_demo.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1
```

Rollback expectation:

- Restore the previous application revision.
- Restore the previous database backup if migrations or data changes are not backward-compatible.
- Rerun health, smoke, governance, release evidence, hosted readiness, and readiness history checks before re-opening the deployment.

## Commercial Handoff

For first paid pilots, use [Code Decision Audit Template](code-decision-audit-template.md). It lets an operator deliver a bounded report without adding runtime license enforcement.

For a complete handoff, attach the latest self-hosted delivery rehearsal summary and readiness evidence history entry. Non-clean states such as `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` must remain visible in customer-facing material.

The recommended pilot claim is:

> DecisionAtlas can be deployed in your environment to analyze selected repositories, surface decision memory, explain why decisions exist, detect bounded drift, and produce reproducible readiness evidence.

The report must include limitations, evidence state, and recommended next actions. It should not imply full SaaS automation, hosted credential custody, or clean readiness unless the evidence supports that claim.
