# 2026-06-10 Update Log

## Commercial Sales Enablement Kit

- Started OpenSpec change `commercial-sales-enablement-kit`.
- Added buyer-facing sales materials:
  - `docs/project/commercial-sales-page-draft.md`
  - `docs/project/commercial-one-page-brief.md`
  - `docs/project/commercial-use-cases.md`
- Updated `docs/project/pilot-customer-delivery-kit.md` and `docs/project/self-hosted-commercial-baseline.md` to reference the sales page, one-page brief, and use-case materials.
- Extended `scripts/ci/verify_pilot_customer_delivery_kit.py` so sales materials are required and commercial boundaries are checked.
- Extended `scripts/ci/build_self_hosted_package.py` and `scripts/ci/verify_self_hosted_package.py` so sales materials are included in the self-hosted package and required by package verification.
- Synced OpenSpec specs:
  - `openspec/specs/commercial-sales-enablement-kit/spec.md`
  - `openspec/specs/pilot-customer-delivery-kit/spec.md`
  - `openspec/specs/offline-self-hosted-release-package/spec.md`

## Commercial Sales Kit Validation

- Targeted pytest:
  - `python -m pytest services/engine/tests/ci/test_pilot_customer_delivery_kit.py services/engine/tests/ci/test_self_hosted_package.py -q --tb=short`
  - Result: `7 passed`
  - Note: pytest cache could not be written in the local restricted environment; tests passed.
- Pilot kit verification:
  - JSON: `.tmp/commercial-sales-pilot-kit-verification.json`
  - Markdown: `.tmp/commercial-sales-pilot-kit-verification.md`
  - Status: `pass`
- Self-hosted commercial sales package:
  - Manifest: `.tmp/commercial-sales-package-manifest.json`
  - Package path: `.tmp/commercial-sales-package/decisionatlas-commercial-sales-kit/`
  - Package verification JSON: `.tmp/commercial-sales-package-verification.json`
  - Package verification Markdown: `.tmp/commercial-sales-package-verification.md`
  - Status: `pass`
- OpenSpec strict validation:
  - `openspec validate --all --strict`
  - Result: `60 passed, 0 failed`

## Browser And Real Repository Validation

- Chromium browser review:
  - Evidence: `.tmp/commercial-sales-browser-review.json`
  - Screenshots:
    - `.tmp/commercial-sales-sales-page-browser.png`
    - `.tmp/commercial-sales-one-page-brief-browser.png`
    - `.tmp/commercial-sales-use-cases-browser.png`
  - Status: `passed`
  - Confirmed required headings and buyer-facing boundaries for all three sales materials.
- Random real GitHub repository rehearsal:
  - Random repo id: `httpx`
  - Repository: `encode/httpx`
  - Evidence: `.tmp/commercial-sales-public-github-import.json`
  - Outcome: `reused`
  - Benchmark ready: `true`
  - Latest successful import: `1025` artifacts, `34` reviewable decisions
- Live real-repo benchmark:
  - JSON: `.tmp/commercial-sales-httpx-live-benchmark.json`
  - Markdown: `.tmp/commercial-sales-httpx-live-benchmark.md`
  - Result: `passed=True`
  - Readiness: `review_ready`
  - Drift: `review_required`

## Environment Notes

- Real stack had to be restarted before random real GitHub rehearsal because API `3001` was initially not reachable.
- Playwright/Chromium required elevated execution in this local Windows environment because sandboxed browser launch returned `spawn EPERM`.
