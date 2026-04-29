## ADDED Requirements

### Requirement: Imported readiness includes repeat-run state and actions
Imported-workspace readiness summaries SHALL include repeat-run state and recommended actions so dashboard and validation surfaces can explain whether the workspace should be opened, synced, rerun, reviewed, or inspected.

#### Scenario: Dashboard shows active import state
- **WHEN** an imported workspace has a queued or running import job
- **THEN** the readiness/dashboard summary SHALL expose active import status, active sync origin, and the active job identifier when available

#### Scenario: Dashboard shows latest completed sync state
- **WHEN** an imported workspace has a completed import or sync
- **THEN** the readiness/dashboard summary SHALL expose latest sync origin, latest sync timestamp, and last import summary in addition to review/why readiness

#### Scenario: Recommended actions distinguish review from sync
- **WHEN** an imported workspace has candidate decisions and also repeat-run actions available
- **THEN** readiness recommended actions SHALL distinguish review-next guidance from sync or full-rerun maintenance actions

#### Scenario: Validation can compare repeat-run state without UI scraping
- **WHEN** operator-guided validation checks a workspace dashboard
- **THEN** it SHALL be able to read active import, latest sync, and recommended action state from product APIs instead of scraping rendered UI text

### Requirement: Imported readiness documents repeat-run limitations
Imported-workspace readiness surfaces SHALL explain limitations that affect repeat-run decisions without implying the workspace is fully ready.

#### Scenario: Evidence-limited workspace can still be synced
- **WHEN** an imported workspace is evidence-limited but has an available incremental sync path
- **THEN** readiness copy SHALL make clear that sync may fetch newer artifacts but does not by itself guarantee accepted decision quality

#### Scenario: Failed latest import keeps prior readiness bounded
- **WHEN** the latest import failed but older workspace data exists
- **THEN** readiness SHALL distinguish the failed latest run from any previously usable review or accepted-decision baseline

#### Scenario: Private access issue blocks sync recommendation
- **WHEN** an imported private workspace has missing or unauthorized access-source state
- **THEN** readiness SHALL recommend setup, rotation, retry, or operator investigation before presenting incremental sync as a normal available action
