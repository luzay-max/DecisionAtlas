## ADDED Requirements

### Requirement: Readiness evidence history supports fresh public repository import rehearsal evidence
Readiness evidence history SHALL support fresh public repository import rehearsal JSON and Markdown as a durable evidence family.

#### Scenario: Fresh import rehearsal evidence is supplied
- **WHEN** readiness history archival receives fresh public repository import rehearsal JSON and Markdown paths
- **THEN** the archive SHALL preserve the selected repository, deterministic seed, fresh-import outcome, workspace, import job, imported artifact count, core-loop status, browser status, limitations, blockers, and linked artifact filenames
- **AND** index and trend summaries SHALL expose the evidence family status without converting warnings into pass.

#### Scenario: Fresh import rehearsal evidence is omitted
- **WHEN** readiness history archival omits fresh public repository import rehearsal evidence
- **THEN** the history entry SHALL mark that evidence family as `not_provided`
- **AND** it SHALL NOT search scratch output for a substitute.
