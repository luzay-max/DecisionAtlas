## 1. Customer Delivery Materials

- [x] 1.1 Add pilot customer delivery kit entry document with one-page product explanation and links to all pilot materials.
- [x] 1.2 Add 10-minute demo script covering import, review, why-search, drift, evidence, and limitations.
- [x] 1.3 Add pilot deployment checklist covering prerequisites, env setup, startup, admin initialization, repository import, readiness evidence, clean install rehearsal, and support handoff.
- [x] 1.4 Add customer FAQ covering data custody, private repo access, roles, evidence, backup/restore, upgrade, support, pricing boundary, and deferred capabilities.
- [x] 1.5 Add Community / Team Self-hosted / Enterprise Self-hosted comparison and pilot delivery email template.

## 2. Verification and Package Integration

- [x] 2.1 Add `scripts/ci/verify_pilot_customer_delivery_kit.py` to emit JSON/Markdown verification evidence.
- [x] 2.2 Update self-hosted package builder and verifier to include pilot delivery kit docs and record a pilot kit evidence lane.
- [x] 2.3 Update self-hosted package guide, commercial baseline, and release package docs to reference the pilot delivery kit.

## 3. Tests and Real Rehearsal

- [x] 3.1 Add pytest coverage for pilot delivery kit verification success.
- [x] 3.2 Add pytest coverage for missing required material or reference producing `blocking`.
- [x] 3.3 Generate real pilot delivery kit verification JSON/Markdown.
- [x] 3.4 Use browser-based operator review to open the delivery kit or verification Markdown and confirm readability.

## 4. OpenSpec, Validation, and Release

- [x] 4.1 Sync final requirements into main specs.
- [x] 4.2 Record the 2026-06-09 update log entry for pilot customer delivery kit.
- [x] 4.3 Run targeted pytest and `openspec validate --all --strict`.
- [x] 4.4 Archive `pilot-customer-delivery-kit`, commit, push, and verify CI.
