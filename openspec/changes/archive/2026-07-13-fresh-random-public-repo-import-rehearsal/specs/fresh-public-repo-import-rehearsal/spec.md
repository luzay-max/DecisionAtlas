## ADDED Requirements

### Requirement: Fresh repository selection is provable
The rehearsal SHALL select a bounded public GitHub repository candidate only after owner-scoped lookup proves that no reusable workspace exists for that repository.

#### Scenario: Random candidate is fresh
- **WHEN** the seeded candidate order includes a repository whose lookup reports `workspace_exists=false`
- **THEN** the rehearsal SHALL select that repository and preserve the seed, ordered candidates, and lookup result in evidence.

#### Scenario: Candidate already has a workspace
- **WHEN** lookup reports that a considered repository already has a workspace in the current owner scope
- **THEN** the rehearsal SHALL record it as reuse-ineligible and continue to another candidate without deleting or rerunning the workspace.

#### Scenario: Candidate pool has no fresh repository
- **WHEN** every candidate is reused, inaccessible, or cannot be checked
- **THEN** the rehearsal SHALL report warning, operator-guided, or blocking status and SHALL NOT claim fresh import success.

### Requirement: Fresh import uses the normal product path
The rehearsal SHALL start the existing full public GitHub import path for the selected repository and SHALL wait for bounded terminal job evidence.

#### Scenario: Fresh import succeeds
- **WHEN** preflight proved no workspace and the import job reaches `succeeded`
- **THEN** evidence SHALL identify the outcome as `fresh_import`, include the repository, workspace slug, job id, imported count, and terminal status, and make the workspace available to downstream validation.

#### Scenario: Lookup races with another import
- **WHEN** the import rehearsal observes reuse after the earlier no-workspace preflight
- **THEN** the rehearsal SHALL preserve the race as non-pass evidence and SHALL NOT relabel the workspace as freshly imported.

#### Scenario: Import fails or times out
- **WHEN** the import job fails, the provider is unavailable, the local stack is unavailable, or the bounded wait expires
- **THEN** the rehearsal SHALL preserve the latest job and classified failure without starting a duplicate import or claiming downstream success.

### Requirement: Fresh workspace feeds the governed core loop
A successful fresh import SHALL be usable by the existing review, Why Search, Drift, guardrail, browser, and release-evidence paths without automatically accepting candidate decisions.

#### Scenario: Fresh workspace has reviewable candidates
- **WHEN** the fresh import succeeds and the review queue contains candidates
- **THEN** core-loop evidence SHALL expose the candidate baseline and identify controlled human review as the next action before accepted-decision claims.

#### Scenario: Fresh workspace has insufficient evidence
- **WHEN** the fresh import succeeds but produces no useful candidate or accepted decisions
- **THEN** the rehearsal SHALL preserve an evidence-limited or warning result rather than treating the importer as failed or inventing a clean core-loop pass.

#### Scenario: Browser validation is attached
- **WHEN** an operator completes human-like browser validation for the fresh workspace
- **THEN** durable readiness evidence SHALL identify the same repository and workspace and preserve browser status separately from machine collector status.

### Requirement: Fresh rehearsal evidence is bounded and auditable
The rehearsal SHALL emit JSON and Markdown that distinguish selection, preflight, import, core-loop, browser, and release-evidence outcomes.

#### Scenario: Evidence is generated
- **WHEN** the rehearsal completes or reaches a classified non-pass state
- **THEN** evidence SHALL include schema version, timestamp, selection mode, seed, candidate outcomes, selected repository, preflight result, import result, downstream status, limitations, and next actions.

#### Scenario: Sensitive material is present in source systems
- **WHEN** repository access, model calls, or application logs involve sensitive values
- **THEN** durable rehearsal evidence SHALL exclude credentials, raw private source, raw model output, and unbounded logs.
