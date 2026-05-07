## 1. Data Model And API Contract

- [x] 1.1 Add a governance rule draft migration for bounded metadata fields covering rule type, extraction reason, review rationale, lifecycle status, and optional supersession reference.
- [x] 1.2 Update the SQLAlchemy model and governance repository to read and write the new rule draft metadata without changing existing document import behavior.
- [x] 1.3 Extend governance rule draft serialization and API request models so review calls can preserve optional bounded review rationale.
- [x] 1.4 Update TypeScript API types and client helpers for the additive rule metadata and review rationale payload.

## 2. Extraction Quality

- [x] 2.1 Add governance Markdown fixture coverage for standards, postmortems, decision records, anti-pattern documents, and ordinary prose that should not create drafts.
- [x] 2.2 Tighten deterministic extraction so generic modal language alone is not sufficient to create a rule draft.
- [x] 2.3 Add document-type-aware rule classification and extraction reason generation for supported governance document types.
- [x] 2.4 Preserve existing severity, scope, rationale, source excerpt, and no-auto-accept behavior while adding the new extraction metadata.

## 3. Review Workflow And UI

- [x] 3.1 Update review API tests for accepting and rejecting rule drafts with stored review rationale and reviewer metadata.
- [x] 3.2 Update the governance page to submit review rationale when accepting or rejecting a pending draft.
- [x] 3.3 Display rule type, extraction reason, source excerpt preview, review rationale, lifecycle metadata, severity, and scope on pending and accepted rule cards.
- [x] 3.4 Add accepted-rule filtering by bounded fields such as scope, severity, rule type, and lifecycle status.
- [x] 3.5 Update governance page tests for rationale submission, metadata rendering, filtering, and no page reload behavior.

## 4. Checker Traceability

- [x] 4.1 Update accepted-rule collection so only accepted active current rules are authoritative checker input.
- [x] 4.2 Include accepted-rule traceability metadata in matched rules and source-linked findings without removing existing checker result fields.
- [x] 4.3 Add checker tests proving pending, rejected, stale, and superseded drafts are non-authoritative.
- [x] 4.4 Add checker tests proving matched accepted rules include source excerpt, review rationale, rule type, extraction reason, and lifecycle metadata.

## 5. Validation

- [x] 5.1 Run engine governance API and checker tests for Markdown ingest, review workflow, extraction quality, and diff checker traceability.
- [x] 5.2 Run web governance page tests for review rationale, accepted-rule filtering, and rule metadata rendering.
- [x] 5.3 Run OpenSpec validation for `improve-governance-knowledge-quality-loop`.
- [x] 5.4 Run the local agent governance guardrail and record any caution or pause evidence before archiving.
