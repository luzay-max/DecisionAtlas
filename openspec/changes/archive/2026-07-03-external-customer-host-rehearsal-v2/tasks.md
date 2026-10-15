## 1. Evidence Collector

- [x] 1.1 Inspect existing self-hosted evidence collectors with CodeGraph/native file context.
- [x] 1.2 Add a customer-host v2 rehearsal collector that reads explicit evidence inputs and writes JSON/Markdown.
- [x] 1.3 Add a sanitized host input template or documented schema for external/customer machine facts.
- [x] 1.4 Preserve missing, warning, operator-guided, and blocking states without converting them to pass.
- [x] 1.5 Support optional readiness-history archival for the generated customer-host v2 bundle.

## 2. Tests And Rehearsal

- [x] 2.1 Add unit tests for clean, missing-template, secret-redaction, and archive behavior.
- [x] 2.2 Run a smoke rehearsal that generates `.tmp` JSON/Markdown.
- [x] 2.3 Run or reuse browser-level self-hosted smoke evidence and link it as a lane.

## 3. Documentation And Specs

- [x] 3.1 Document the customer-host v2 rehearsal command, template, evidence boundary, and rerun conditions.
- [x] 3.2 Update the completion taskbook and 2026-07-03 update log.
- [x] 3.3 Sync OpenSpec main specs with the new requirements.

## 4. Validation

- [x] 4.1 Run targeted pytest tests.
- [x] 4.2 Run the relevant browser smoke or self-hosted team browser rehearsal.
- [x] 4.3 Run OpenSpec strict validation for the change and all specs.
