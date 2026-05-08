## ADDED Requirements

### Requirement: Real-repository value reports are optional hosted-preview evidence
The system SHALL treat live real-repository value benchmark reports as optional hosted-preview credibility evidence that can support external discussions without becoming a prerequisite for the stable public walkthrough or default CI.

#### Scenario: Preview checklist marks real-repo value report optional
- **WHEN** hosted preview readiness references live real-repository validation
- **THEN** it SHALL classify JSON and Markdown value reports as optional operator-provided evidence rather than required guided-demo readiness

#### Scenario: Report status is summarized without committing stale output
- **WHEN** an operator generates a live real-repository value benchmark report for preview evidence
- **THEN** guidance SHALL tell the operator to summarize or attach the dated report externally and avoid committing default `.tmp/` generated reports as durable evidence

#### Scenario: Operational blockers do not block public demo
- **WHEN** live real-repository validation reports missing workspaces, provider failures, GitHub/network failure, or operational blockers
- **THEN** hosted preview readiness SHALL treat those outcomes as optional-lane limitations unless the external walkthrough explicitly depends on showing that repository
