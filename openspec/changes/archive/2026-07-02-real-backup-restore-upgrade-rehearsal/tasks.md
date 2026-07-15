## 1. Real Rehearsal Collector

- [x] 1.1 Add a real backup/restore/upgrade rehearsal script that operates only inside an owned scratch root.
- [x] 1.2 Implement scratch source creation, backup artifact generation, restore target creation, and restore integrity comparison.
- [x] 1.3 Record upgrade transition metadata, post-upgrade validation status, rollback plan status, blockers, limitations, and recommended next actions.
- [x] 1.4 Add path-safety checks that reject source, backup, restore, or working paths outside the owned scratch root.
- [x] 1.5 Add redaction checks for token-like values, `.env` secret assignments, credentialed database URLs, private keys, raw backup markers, and private repository snippets.

## 2. Downstream Evidence Integration

- [x] 2.1 Update backup/restore/upgrade docs to distinguish non-destructive verifier evidence from real scratch rehearsal evidence.
- [x] 2.2 Update self-hosted delivery rehearsal material to accept and disclose optional real continuity evidence.
- [x] 2.3 Update team handoff report generation to summarize real continuity evidence without copying sensitive content.
- [x] 2.4 Update Code Decision Audit report generation to summarize real continuity evidence and preserve missing evidence as non-pass.
- [x] 2.5 Include the real continuity rehearsal script in self-hosted package expectations when appropriate.

## 3. Validation

- [x] 3.1 Add unit tests for successful scratch backup/restore validation and generated JSON/Markdown evidence.
- [x] 3.2 Add unit tests for restore mismatch, missing inputs, unsafe paths, and redaction failures.
- [x] 3.3 Add tests for handoff and audit report integration with supplied, missing, and unsafe real continuity evidence.
- [x] 3.4 Run relevant Python tests for CI/evidence/report scripts.
- [x] 3.5 Run OpenSpec strict validation for the change and all specs.
- [x] 3.6 Record implementation and validation evidence in the project update log.
