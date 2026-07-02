## 1. Evidence Input And Collector

- [ ] 1.1 Add an external install evidence input template with host profile, package identity, startup checks, health checks, browser smoke, repository import, readiness evidence, limitations, and redaction acknowledgement fields.
- [ ] 1.2 Implement a local external install evidence collector/verifier that reads the explicit input file and writes JSON and Markdown evidence.
- [ ] 1.3 Classify lane statuses as `passed`, `warning`, `operator_guided`, `not_provided`, or `blocked` without synthesizing pass evidence from local state.
- [ ] 1.4 Add redaction checks for token-like values, provider key markers, `.env` secret assignments, private key markers, raw backup content markers, and raw private repository snippets.

## 2. Downstream Evidence Integration

- [ ] 2.1 Update clean install rehearsal material to distinguish local clean workspace checks from external/customer-host install evidence.
- [ ] 2.2 Update self-hosted delivery rehearsal generation to accept optional external install evidence and preserve missing evidence as `operator_guided` or `not_provided`.
- [ ] 2.3 Update team handoff report generation to summarize external install evidence status without copying sensitive content.
- [ ] 2.4 Update Code Decision Audit report generation to reference external install readiness when sanitized evidence is supplied.

## 3. Documentation And Package Surface

- [ ] 3.1 Add operator documentation for collecting external install evidence from a clean VM, another machine, or customer-controlled host.
- [ ] 3.2 Update self-hosted commercial/package guidance to state that package verification and local clean install are not customer-host proof.
- [ ] 3.3 Include the external evidence template and documentation in package verification expectations when appropriate.

## 4. Validation

- [ ] 4.1 Add unit tests for external evidence generation, lane classification, missing input, missing lanes, and redaction failures.
- [ ] 4.2 Add tests for handoff and audit report integration with provided, missing, and unsafe external evidence.
- [ ] 4.3 Run relevant Python tests for CI/evidence/report scripts.
- [ ] 4.4 Run OpenSpec strict validation for the change and all specs.
- [ ] 4.5 Record implementation and validation evidence in the project update log.
