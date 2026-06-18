## 1. Proposal Kit Materials

- [x] 1.1 Add pilot commercial proposal kit entry document with scope, buyer, offer, evidence, acceptance, support, renewal, and upgrade links.
- [x] 1.2 Add paid pilot quote assumptions template that clearly marks prices and terms as editable draft assumptions.
- [x] 1.3 Add paid pilot acceptance checklist tied to package, release, readiness, benchmark, private-repo, and backup/restore/upgrade evidence.
- [x] 1.4 Add support response boundary and renewal/upgrade path material without promising SaaS billing, hosted multi-tenancy, Marketplace OAuth, or runtime license enforcement.

## 2. Verification And Package Integration

- [x] 2.1 Add `scripts/ci/verify_pilot_commercial_proposal_kit.py` to emit JSON/Markdown verification evidence.
- [x] 2.2 Add tests for proposal kit verifier success, missing required reference, and forbidden customer-private material.
- [x] 2.3 Update self-hosted package builder and verifier to include proposal kit docs and a proposal-kit evidence lane.
- [x] 2.4 Update package guide, pilot customer delivery kit, and self-hosted commercial baseline docs to reference the proposal kit.

## 3. Validation And Real Evidence

- [x] 3.1 Run targeted pytest coverage for the new verifier and updated package verification.
- [x] 3.2 Run `openspec validate pilot-commercial-proposal-kit --type change --strict` and `openspec validate --all --strict`.
- [x] 3.3 Generate `.tmp` JSON/Markdown proposal kit verification evidence.
- [x] 3.4 Use Chromium/Playwright to render the proposal kit material and verify customer-readable content.
- [x] 3.5 Run or reuse a live public GitHub repository evidence check to keep real-repo validation attached to commercial claims.
- [x] 3.6 Run governance guardrail and record whether the state is continue, caution, or pause.

## 4. Handoff

- [x] 4.1 Record this change in the 2026-06-18 update log with commands, evidence, limitations, and generated artifacts.
- [x] 4.2 Sync delta specs to main specs before archive.
- [x] 4.3 Archive `pilot-commercial-proposal-kit`, commit, push, and verify CI.
