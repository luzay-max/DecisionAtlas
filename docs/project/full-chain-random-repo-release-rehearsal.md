# Full-Chain Random Repo Release Rehearsal

Date: 2026-07-03

## Purpose

This rehearsal is the current top-level delivery checkpoint. It composes random real GitHub repository diagnosis, release rehearsal, customer-host v2, browser self-hosted flow, and readiness history into one customer-safe evidence bundle.

## Commands

First refresh random real repository and release evidence:

```powershell
python scripts\ci\collect_release_rehearsal_evidence.py `
  --label full-chain-random-repo-release-source `
  --run-multi-repo-diagnosis `
  --random-count 2 `
  --random-seed 7303 `
  --output-json .tmp\release-rehearsal-evidence.json `
  --output-markdown .tmp\release-rehearsal-evidence.md `
  --multi-repo-output-json .tmp\multi-repo-live-diagnosis.json `
  --multi-repo-output-markdown .tmp\multi-repo-live-diagnosis.md
```

Then refresh customer-host v2 evidence:

```powershell
python scripts\ci\collect_external_customer_host_rehearsal_v2.py `
  --label full-chain-customer-host-v2-source `
  --host-input-json templates\external-customer-host-rehearsal-v2.example.json `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --clean-install-json .tmp\clean-self-hosted-install-rehearsal.json `
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json `
  --release-rehearsal-json .tmp\release-rehearsal-evidence.json `
  --readiness-history-json docs\evidence\readiness\index.json `
  --output-json .tmp\external-customer-host-rehearsal-v2.json `
  --output-markdown .tmp\external-customer-host-rehearsal-v2.md
```

Run the browser rehearsal:

```powershell
PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line
```

Generate the full-chain bundle:

```powershell
python scripts\ci\collect_full_chain_random_repo_release_rehearsal.py `
  --label full-chain-random-repo-release-rehearsal-smoke `
  --multi-repo-diagnosis-json .tmp\multi-repo-live-diagnosis.json `
  --release-rehearsal-json .tmp\release-rehearsal-evidence.json `
  --customer-host-v2-json .tmp\external-customer-host-rehearsal-v2.json `
  --readiness-history-json docs\evidence\readiness\index.json `
  --browser-status passed `
  --browser-summary "team-self-hosted-rehearsal.spec.ts passed against local self-hosted stack" `
  --archive-history `
  --output-json .tmp\full-chain-random-repo-release-rehearsal.json `
  --output-markdown .tmp\full-chain-random-repo-release-rehearsal.md
```

## Current Evidence

- Random real repositories: `n8n-io/n8n`, `Textualize/rich`
- Full-chain JSON: `.tmp/full-chain-random-repo-release-rehearsal.json`
- Full-chain Markdown: `.tmp/full-chain-random-repo-release-rehearsal.md`
- Durable archive: `docs/evidence/readiness/2026-07-03-full-chain-random-repo-release-rehearsal-smoke/`
- Current status: `warning`
- Blocking lanes: `0`
- Browser lane: `pass`

## Evidence Boundary

This is a full-chain rehearsal, not a final customer production acceptance. The warning status is expected while random real repository diagnosis, release rehearsal, customer-host v2, and readiness history still contain non-clean lanes.

The customer-host lane still uses the example template. Replace it with a real customer or non-developer host template before claiming customer-controlled host proof.
