## 1. Live analysis entry and workspace routing

- [x] 1.1 Add a live-analysis submission path that accepts a public GitHub repository reference or URL.
- [x] 1.2 Create or reuse imported workspaces by normalized repository identity so live runs stay separate from the guided demo workspace.
- [x] 1.3 Route users from live-analysis submission into the corresponding imported workspace and preserve existing workspace-centric navigation.

## 2. Stage-aware job execution and outcome reporting

- [x] 2.1 Extend import job persistence and API responses with stage-aware status for artifact import, indexing, extraction, and terminal states.
- [x] 2.2 Add broad failure classification and insufficient-evidence outcome reporting for live analysis runs.
- [x] 2.3 Update dashboard and related live-analysis surfaces to display stage context, terminal summaries, and honest sparse-result messaging.

## 3. Validation and proof of real capability

- [x] 3.1 Add backend and web tests covering live workspace creation or reuse, stage-aware job responses, and failure-versus-insufficient-evidence behavior.
- [x] 3.2 Define a small public benchmark repository set and add repeatable validation expectations for the live-analysis path.
- [x] 3.3 Update README and project docs to explain the supported scope of real public repository analysis and its known limitations.
