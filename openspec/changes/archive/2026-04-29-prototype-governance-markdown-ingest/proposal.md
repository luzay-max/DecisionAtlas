## Why

DecisionAtlas is ready to add the first AI governance knowledge-layer slice: users need a way to import human-authored Markdown standards, roadmaps, postmortems, and decisions so future AI checks can stay aligned with project direction. This stage should capture governance knowledge in a reviewable form without letting AI automatically enforce or rewrite project rules.

## What Changes

- Add owner-scoped Markdown governance document ingest for project standards, coding guidelines, architecture policies, roadmaps, postmortems, checklists, decision records, anti-patterns, release policies, and security policies.
- Store governance documents with metadata such as title, document type, scope, source path, status, and content hash.
- Extract deterministic rule drafts from Markdown headings, bullets, and explicit severity/scope markers.
- Provide human review actions for rule drafts: accept or reject.
- Persist accepted governance rules with source-document traceability for later checker work.
- Add a minimal product/API surface to list documents, inspect drafts, and review governance rules.
- Keep AI/diff enforcement out of scope for this first slice.

## Capabilities

### New Capabilities

- `governance-markdown-ingest`: Import Markdown governance documents, classify them, create reviewable rule drafts, and persist accepted governance rules with source traceability.

### Modified Capabilities

- None.

## Impact

- Engine database models, migration, repositories, and API routes for governance documents and rule drafts.
- API proxy routes and web client helpers.
- Minimal web surface for ingesting Markdown and reviewing drafts.
- Tests for ingest, classification, draft extraction, review actions, and product rendering.
- Documentation updates for Stage 4 MVP boundaries and follow-on checker work.
