## Why

Markdown governance documents can already create human-reviewed rule drafts, but the current deterministic extraction is too broad for high-signal governance use: ordinary prose can become a draft, review decisions do not capture rationale, and accepted-rule impact is not easy enough to trace from review UI through checker output. This change tightens the governance knowledge loop so humans and AI agents can trust accepted rules as durable advisory input.

## What Changes

- Improve deterministic rule-draft extraction so rule-like sections require stronger signals than generic modal language.
- Preserve richer extraction context for each draft, including document-type-aware rule classification and a concise reason why the section was extracted.
- Add review rationale capture for accept and reject decisions so human judgment is preserved with the rule draft.
- Improve the governance review surface so reviewers can filter accepted rules and inspect source evidence, extraction reasons, and review rationale quickly.
- Prepare stale or superseded rule lifecycle metadata without introducing automatic rule replacement or full knowledge graph UI.
- Add fixtures and tests for standards, postmortems, decision records, and anti-pattern governance documents.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `governance-markdown-ingest`: Tighten deterministic rule-draft extraction, add document-type-aware rule metadata, capture review rationale, expose accepted-rule filtering, and prepare stale or superseded lifecycle metadata.
- `governance-diff-checker`: Preserve enough accepted-rule metadata in matched-rule and finding output for reviewers and AI agents to trace checker impact back to source excerpts and human review rationale.

## Impact

- Engine governance ingest logic, repository model, API serialization, and database schema for rule draft metadata.
- Governance review API contract for accept and reject rationale.
- Web governance page state, filters, rule cards, and tests.
- Governance diff checker matched-rule serialization and tests.
- OpenSpec specs and fixtures covering rule extraction quality, review traceability, and authoritative accepted-rule behavior.
