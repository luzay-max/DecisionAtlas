# External Customer Host Rehearsal v2

Date: 2026-07-03

## Purpose

This rehearsal turns customer-host readiness from scattered local evidence into one customer-readable evidence bundle. It is designed for a solo/self-hosted delivery model where an operator or customer can run checks on a non-developer machine and provide sanitized facts without sharing secrets.

## Command

```powershell
python scripts\ci\collect_external_customer_host_rehearsal_v2.py `
  --label external-customer-host-rehearsal-v2-smoke `
  --host-input-json templates\external-customer-host-rehearsal-v2.example.json `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --clean-install-json .tmp\clean-self-hosted-install-rehearsal.json `
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json `
  --release-rehearsal-json .tmp\release-rehearsal-evidence.json `
  --readiness-history-json docs\evidence\readiness\index.json `
  --archive-history `
  --output-json .tmp\external-customer-host-rehearsal-v2.json `
  --output-markdown .tmp\external-customer-host-rehearsal-v2.md
```

## Template

Use `templates/external-customer-host-rehearsal-v2.example.json` as the customer/operator input shape.

The file records:

- host profile
- package identity
- commands run
- health checks
- browser smoke summary
- redaction acknowledgement
- limitations

Do not paste tokens, `.env` values, private repository content, raw logs, database backups, or private keys into the template.

## Evidence Boundary

This v2 collector does not mutate customer infrastructure. It reads explicit source evidence and produces a compact bundle.

The output status can be `pass`, `warning`, or `blocking`. Missing, operator-guided, warning, and blocking lanes remain visible. A local clean install or example template is not the same as proof from a real customer-controlled machine.

## Current Smoke Evidence

- JSON: `.tmp/external-customer-host-rehearsal-v2.json`
- Markdown: `.tmp/external-customer-host-rehearsal-v2.md`
- Readiness history: `docs/evidence/readiness/2026-07-03-external-customer-host-rehearsal-v2-smoke/`
- Current smoke status: `warning`
- Current boundary: generated from the repository template plus existing local evidence; it is suitable as rehearsal plumbing evidence, not final customer-host proof.

## Browser Evidence

The same run was paired with the self-hosted team browser rehearsal:

```powershell
PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm --filter @decisionatlas/web exec playwright test team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line
```

The browser rehearsal validates a human-like path through team setup, workspace membership, and viewer read-only review behavior.
