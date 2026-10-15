# Pilot Customer Trial Package

Date: 2026-07-04

## Summary

The pilot customer trial package turns existing DecisionAtlas self-hosted pilot materials and evidence outputs into one operator-facing handoff bundle.

It does not prove a real customer-controlled host by itself. It shows what is ready, what is missing, what is operator-guided, and what evidence must be replaced before a clean customer-host claim.

## Generated Artifacts

- JSON: `.tmp/pilot-customer-trial-package.json`
- Markdown: `.tmp/pilot-customer-trial-package.md`
- Bundle directory: `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/`
- Bundle README: `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/README.md`
- Operator checklist: `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/operator-checklist.md`
- Evidence manifest: `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/evidence-manifest.json`
- Evidence manifest Markdown: `.tmp/pilot-customer-trial-package/pilot-customer-trial-package/evidence-manifest.md`

## Current Smoke Result

- Status: `warning`
- Blocking lanes: `0`
- Reason: current real external host trial evidence is still `template_or_placeholder`, and several optional evidence lanes remain `not_provided`.

This is the expected state until the project is run on a real non-developer machine, customer VM, friend machine, or independent server.

## How To Generate

```powershell
python scripts\ci\collect_pilot_customer_trial_package.py `
  --pilot-delivery-verification-json .tmp\pilot-customer-delivery-kit-verification.json `
  --commercial-proposal-verification-json .tmp\pilot-commercial-proposal-kit-verification.json `
  --real-external-host-trial-json .tmp\real-external-host-trial-evidence.json `
  --full-chain-json .tmp\full-chain-random-repo-release-rehearsal.json `
  --customer-host-v2-json .tmp\external-customer-host-rehearsal-v2.json `
  --readiness-history-json docs\evidence\readiness\index.json `
  --output-json .tmp\pilot-customer-trial-package.json `
  --output-markdown .tmp\pilot-customer-trial-package.md `
  --bundle-dir .tmp\pilot-customer-trial-package\pilot-customer-trial-package `
  --clean-bundle
```

## What Operators Should Do Next

- Replace template-only real external host evidence with sanitized observations from a real external/customer-controlled host.
- Rerun customer-host v2, full-chain random repo release rehearsal, and real external host trial evidence.
- Regenerate this package and check whether `warning` lanes decreased.
- Keep agreements, customer identifiers, credentials, raw logs, private repository content, payment details, and legal terms outside the public repository.
