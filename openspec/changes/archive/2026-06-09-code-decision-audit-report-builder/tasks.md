## 1. Implementation

- [x] Add a Code Decision Audit report builder script.
- [x] Preserve non-clean and missing evidence states in JSON/Markdown output.
- [x] Update Code Decision Audit and release/self-hosted docs with generation commands.

## 2. Verification

- [x] Add pytest coverage for supplied evidence, omitted evidence, warning preservation, and secret/local-path redaction.
- [x] Generate `.tmp/code-decision-audit-report.json` and `.tmp/code-decision-audit-report.md` from current evidence.
- [x] Run targeted pytest and OpenSpec validation.
- [x] Run browser-style review attempt and record the environment blocker.

Note: direct `file://` review of generated Markdown was blocked by the in-app browser URL policy. A real Chromium localhost smoke was attempted, but the current real stack was not running and Docker Desktop was unavailable, so `127.0.0.1:3000` and `127.0.0.1:3001` returned connection refused.
