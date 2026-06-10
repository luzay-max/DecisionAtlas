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

## Final Post-Commercialization Roadmap

- Started OpenSpec change `final-post-commercialization-roadmap`.
- Added final roadmap:
  - `docs/plans/2026-06-10-decisionatlas-final-post-commercialization-roadmap.md`
- The roadmap consolidates:
  - 5.8 optimization plan completion state
  - 5.9 commercialization/productization completion state
  - current evidence-backed status
  - remaining gaps
  - next priorities and difficulty
  - deferred SaaS/commercial infrastructure lanes
- Recommended next OpenSpec change:
  - `private-repo-pilot-evidence-template`
- Validation:
  - `openspec validate --all --strict`: `61 passed, 0 failed`
  - Browser review: `.tmp/final-post-commercialization-roadmap-browser-review.json`
  - Screenshot: `.tmp/final-post-commercialization-roadmap-browser.png`
  - Browser status: `passed`

## Real Stack AI And Browser Rehearsal

- Verified the running real stack after Docker startup:
  - Engine health: `http://127.0.0.1:8000/health` returned `{"ok":true}`
  - API health: `http://127.0.0.1:3001/health` returned `{"ok":true}`
  - Web: `http://127.0.0.1:3000` returned HTTP `200`
- Verified live model provider usage:
  - Evidence: `.tmp/model-provider-smoke.json`
  - Provider mode: `openai_compatible`
  - Embedding mode: `fake`
  - Result: `passed`
  - Note: the smoke output records only provider mode, model label, boolean result, and latency; it does not store credentials or raw model output.
- Verified real browser routes with in-app Browser and Chromium:
  - Evidence: `.tmp/real-stack-browser-smoke.json`
  - Screenshot: `.tmp/real-stack-browser-smoke.png`
  - Routes: home, review, why search, drift, team admin
  - Result: `passed`
- Generated release/readiness evidence:
  - Guardrail summary: `.tmp/guardrail-summary.json`, `.tmp/guardrail-summary.txt`
  - Enforcement preview: `.tmp/guardrail-enforcement-preview.json`
  - Benchmark snapshot: `.tmp/current-real-repo-benchmark-snapshot.json`
  - Benchmark comparison: `.tmp/real-repo-benchmark-comparison.json`, `.tmp/real-repo-benchmark-comparison.md`
  - Release evidence: `.tmp/release-evidence.json`, `.tmp/release-evidence.md`, status `passed`
  - Hosted/operator readiness: `.tmp/hosted-operator-readiness.json`, `.tmp/hosted-operator-readiness.md`, public walkthrough status `operator_guided`
- Archived readiness history:
  - Entry: `docs/evidence/readiness/2026-06-10-2026-06-10-real-stack-ai-browser-rehearsal/`
  - Index: `docs/evidence/readiness/index.json`, `docs/evidence/readiness/index.md`
  - Trend: `docs/evidence/readiness/trend.md`
  - Status: `warning`
  - Reason: local `127.0.0.1` URLs are valid for local rehearsal but still operator-guided for external hosted preview claims.

## Seeded Demo Reset Fix

- Real rehearsal found that `scripts/demo/reset_seeded_demo.py` failed against Postgres when `review_audit_events` referenced the demo workspace.
- Fixed reset cleanup so demo workspace review audit events are deleted before deleting the workspace.
- Added regression coverage in `services/engine/tests/test_seeded_demo_recovery.py`.
- Validation:
  - `python -m uv run pytest tests\test_seeded_demo_recovery.py -q`: `2 passed`
  - Real Postgres reset/check completed and regenerated `.tmp/seeded-demo-readiness.json` with `ready: true`

## Private Repo Pilot Evidence Template

- Started and completed OpenSpec change `private-repo-pilot-evidence-template`.
- Added customer-safe private repository pilot evidence materials:
  - `docs/project/private-repo-pilot-evidence-template.md`
  - `docs/project/private-repo-pilot-evidence-example.md`
  - `templates/private-repo-pilot-evidence.example.json`
- Added verifier and regression coverage:
  - `scripts/ci/verify_private_repo_pilot_evidence.py`
  - `services/engine/tests/ci/test_private_repo_pilot_evidence.py`
- Updated pilot and self-hosted package materials so private-repo pilot claims require sanitized evidence and preserve `operator_guided` when real customer-host proof is absent:
  - `docs/project/pilot-customer-delivery-kit.md`
  - `docs/project/self-hosted-commercial-baseline.md`
  - `scripts/ci/verify_pilot_customer_delivery_kit.py`
  - `scripts/ci/build_self_hosted_package.py`
  - `scripts/ci/verify_self_hosted_package.py`
- Generated current evidence:
  - Private-repo evidence verifier: `.tmp/private-repo-pilot-evidence-verification.json`, `.tmp/private-repo-pilot-evidence-verification.md`, status `operator_guided`, blockers `[]`
  - Pilot kit verifier: `.tmp/pilot-customer-delivery-kit-verification.json`, `.tmp/pilot-customer-delivery-kit-verification.md`, status `pass`
  - Self-hosted package manifest: `.tmp/private-repo-pilot-package-manifest.json`
  - Self-hosted package verifier: `.tmp/private-repo-package-verification.json`, `.tmp/private-repo-package-verification.md`, status `pass`
  - Browser readability evidence: `.tmp/private-repo-pilot-evidence-browser-review.json`
  - Chromium screenshot: `.tmp/private-repo-pilot-evidence-browser-review.png`
- Real stack check after Docker startup:
  - `scripts/dev/start-real-stack.ps1 -ResetSeededDemo` completed successfully.
  - Engine health: `http://127.0.0.1:8000/health` returned `{"ok":true}`
  - API health: `http://127.0.0.1:3001/health` returned `{"ok":true}`
  - Web: `http://127.0.0.1:3000` returned HTTP `200`
  - Browser evidence: `.tmp/private-repo-pilot-real-stack-browser.json`
- Public GitHub stand-in validation:
  - Repository: `encode/httpx`
  - Evidence: `.tmp/private-repo-pilot-public-github-standin.json`, `.tmp/private-repo-pilot-public-github-standin.md`
  - Outcome: `reused`
  - Benchmark ready: `true`
  - Latest successful import: `1025` artifacts, `34` reviewable decisions
  - Limitation: this is only a non-sensitive public-repo live validation habit check; it is not proof that any real private repository was evaluated.
- Validation:
  - `python scripts\ci\verify_private_repo_pilot_evidence.py --evidence-json templates\private-repo-pilot-evidence.example.json --evidence-markdown docs\project\private-repo-pilot-evidence-example.md --output-json .tmp\private-repo-pilot-evidence-verification.json --output-markdown .tmp\private-repo-pilot-evidence-verification.md --generated-at 2026-06-10T00:00:00+00:00`: `operator_guided`, blockers `[]`
  - `python -m uv run pytest tests\ci\test_private_repo_pilot_evidence.py tests\ci\test_pilot_customer_delivery_kit.py tests\ci\test_self_hosted_package.py -q`: `10 passed`
  - `openspec validate private-repo-pilot-evidence-template --type change --strict`: valid
  - `openspec validate --all --strict`: `62 passed, 0 failed`
  - `python scripts\governance\agent_guardrail.py --summary`: `caution`
- Guardrail handoff:
  - Evidence: `.tmp/private-repo-pilot-guardrail.json`, `.tmp/private-repo-pilot-guardrail-summary.txt`
  - Diff check: `pass`
  - Drift report: `drift_detected`
  - Action taken: disclosed the advisory caution, kept `.tmp` generated artifacts uncommitted, and recorded that private-repo proof must be generated only on the customer-controlled host.
