## 1. Rehearsal Entry Point

- [x] 1.1 Inspect existing import APIs, workspace lookup, and benchmark runner inputs for public GitHub repositories.
- [x] 1.2 Add a repeatable public GitHub import rehearsal command or script that targets a curated repository by id and creates or reuses its expected workspace.
- [x] 1.3 Ensure the rehearsal reports bounded setup outcomes: created, reused, missing_workspace, provider_failure, local_stack_failure, or operator_guided.

## 2. Evidence Integration

- [x] 2.1 Generate JSON evidence for the import/reuse setup path, workspace slug, repository id, bounded outcome, and next action.
- [x] 2.2 Generate operator-readable Markdown evidence that mirrors the JSON evidence.
- [x] 2.3 Ensure benchmark execution after rehearsal treats imported workspaces as product evidence and selected-but-not-imported workspaces as non-pass setup evidence.

## 3. Documentation

- [x] 3.1 Update self-hosted rehearsal documentation to require public repository import/reuse proof before claiming live benchmark evidence.
- [x] 3.2 Update the 2026-06-05 update log or current project log with the rehearsal result and any limitations.

## 4. Verification

- [x] 4.1 Add or update tests for public import rehearsal outcome classification without requiring live GitHub access.
- [x] 4.2 Run OpenSpec strict validation for the change.
- [x] 4.3 Run targeted backend/script tests.
- [x] 4.4 Run the real local-stack rehearsal when services are available and record whether `fastapi/fastapi` imports, reuses, or remains operator-guided.
