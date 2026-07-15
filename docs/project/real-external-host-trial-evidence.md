# Real External Host Trial Evidence

Date: 2026-07-03

## Summary

This change adds a stricter evidence gate for real external or customer-controlled host trial claims.

The existing customer-host v2 collector can prove that the host evidence pipeline works. This new collector answers a stricter question: whether the supplied evidence is strong enough to claim a real external/customer-controlled host trial, or whether it is still sample/template/local smoke evidence.

## What Was Added

- `scripts/ci/collect_real_external_host_trial_evidence.py`
- `.tmp/real-external-host-trial-evidence.json`
- `.tmp/real-external-host-trial-evidence.md`
- Readiness history family: `real_external_host_trial_evidence`
- Tests for clean evidence, placeholder/template evidence, missing input, redaction blocking, and readiness history archival.

## Evidence Boundary

Current smoke uses `templates/external-customer-host-rehearsal-v2.example.json`, so the result is expected to be `warning`.

This is correct. The collector detected placeholder/template values such as `fill-me`, `customer-or-operator-name`, `optional`, and sample limitations. It preserved the boundary that example or local evidence is not real customer-host proof.

## Smoke Result

- JSON: `.tmp/real-external-host-trial-evidence.json`
- Markdown: `.tmp/real-external-host-trial-evidence.md`
- Readiness history: `docs/evidence/readiness/2026-07-03-real-external-host-trial-evidence-smoke/`
- Status: `warning`
- Host proof level: `template_or_placeholder`
- Blocking lanes: `0`

## How To Run

```powershell
python scripts\ci\collect_real_external_host_trial_evidence.py `
  --host-input-json templates\external-customer-host-rehearsal-v2.example.json `
  --customer-host-v2-json .tmp\external-customer-host-rehearsal-v2.json `
  --full-chain-json .tmp\full-chain-random-repo-release-rehearsal.json `
  --output-json .tmp\real-external-host-trial-evidence.json `
  --output-markdown .tmp\real-external-host-trial-evidence.md
```

To archive:

```powershell
python scripts\ci\collect_real_external_host_trial_evidence.py `
  --host-input-json <sanitized-real-external-host-json> `
  --customer-host-v2-json .tmp\external-customer-host-rehearsal-v2.json `
  --full-chain-json .tmp\full-chain-random-repo-release-rehearsal.json `
  --archive-history `
  --archive-label real-external-host-trial-evidence
```

## Next Real Validation

The next meaningful product validation is to run the self-hosted package on a real non-developer machine, customer VM, friend machine, or independent server, then replace the example template with sanitized observations from that host.

Do not paste tokens, `.env` values, raw private repository contents, raw database backups, raw model output, or raw customer logs into the host evidence input.
