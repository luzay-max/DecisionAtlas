## 1. Collector

- [x] 1.1 Inspect existing release/customer-host/multi-repo evidence collectors with CodeGraph and file context.
- [x] 1.2 Add a full-chain rehearsal collector that reads source evidence and writes JSON/Markdown.
- [x] 1.3 Include random real GitHub repository IDs and aggregate diagnosis status when available.
- [x] 1.4 Include release rehearsal, customer-host v2, browser flow, and readiness-history lanes.
- [x] 1.5 Support optional readiness-history archival.

## 2. Tests And Evidence

- [x] 2.1 Add tests for clean, missing evidence, random repo summary, and archival behavior.
- [x] 2.2 Run random real public GitHub repository diagnosis through the existing release rehearsal path or source evidence.
- [x] 2.3 Run the browser-level self-hosted team rehearsal and record it as a lane.
- [x] 2.4 Generate `.tmp/full-chain-random-repo-release-rehearsal.json/md` and durable readiness evidence.

## 3. Docs And Specs

- [x] 3.1 Document the full-chain command, evidence boundary, and rerun conditions.
- [x] 3.2 Update the 2026-07-03 update log and completion taskbook.
- [x] 3.3 Sync OpenSpec main specs.

## 4. Validation

- [x] 4.1 Run targeted pytest tests.
- [x] 4.2 Run browser rehearsal.
- [x] 4.3 Run OpenSpec strict validation for the change and all specs.
