## Why

Real imported repositories currently rely on issues, pull requests, and commits alone, which often leaves small or documentation-heavy projects with too little evidence to form useful decision memory. We need to ingest the highest-signal repository documents so real workspaces produce more meaningful candidates, why-answers, and import summaries without turning v0.2 into a full source-code analysis system.

## What Changes

- Expand GitHub repository ingest to include a narrow set of high-signal markdown documents from the remote repo, starting with top-level decision-oriented files and selected documentation paths.
- Add import summary visibility so the product can explain what was imported, what was skipped, and why a real workspace may still have low decision coverage.
- Improve real-workspace empty and low-signal states so “no candidate decisions” is explained as an evidence limitation rather than looking like a broken import.
- Keep the ingest scope intentionally conservative: no large-scale source code ingestion, no GitHub App auth changes, and no changes to the existing citation-first answer contract.

## Capabilities

### New Capabilities
- `repository-document-ingest`: Import high-signal markdown repository documents alongside issues, pull requests, and commits, and surface import transparency for real workspaces.

### Modified Capabilities
- None.

## Impact

- Affected engine ingest code in `services/engine/app/ingest/`
- Affected import APIs and import job summaries exposed through engine and Node API
- Affected dashboard and related real-workspace empty states in `apps/web`
- Additional ingest tests for remote document selection, import summaries, and low-signal workspace behavior
