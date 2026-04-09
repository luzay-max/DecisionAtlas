## MODIFIED Requirements

### Requirement: Imported drift evaluation is operationally usable
The system SHALL expose drift evaluation state for imported workspaces so users can run it intentionally, interpret the result correctly, distinguish stronger supersession signals from broader review-only follow-up material, avoid repeated weak alerts that all represent the same accepted-decision thread, avoid stale alert conclusions from earlier reevaluation passes, avoid over-labeling implementation substitutions as decision replacement, and keep implementation-heavy bugfixes and lifecycle fixes out of the stronger replacement path unless clearer decision replacement evidence is present.

#### Scenario: User can evaluate drift for an imported workspace
- **WHEN** the user requests drift evaluation for an imported workspace
- **THEN** the system SHALL execute drift evaluation for that workspace and report whether alerts were created

#### Scenario: Drift page distinguishes unevaluated from no-alert result
- **WHEN** the imported workspace drift surface is shown before or after evaluation
- **THEN** the system SHALL distinguish between a workspace that has not been evaluated yet and a workspace that was evaluated but produced no current alerts

#### Scenario: Drift alert semantics distinguish stronger from weaker signals
- **WHEN** imported drift alerts are shown after evaluation
- **THEN** the product SHALL distinguish stronger possible-supersession signals from broader needs-review follow-up signals instead of presenting both with equally strong replacement semantics

#### Scenario: Repeated weak follow-up alerts are compact
- **WHEN** several later artifacts all reflect implementation follow-up around the same accepted decision
- **THEN** the imported drift surface SHALL present that material in a compact grouped or deduplicated form instead of rendering many nearly identical weak alerts

#### Scenario: Reevaluation replaces stale alert conclusions
- **WHEN** a later drift reevaluation changes the semantic outcome for an imported artifact-decision thread
- **THEN** the imported drift surface SHALL present only the latest alert conclusion instead of showing both the stale prior alert and the new replacement

#### Scenario: Implementation substitution stays weaker than decision replacement
- **WHEN** an imported drift alert is driven by lower-level implementation substitution rather than clearer decision-level replacement
- **THEN** the imported experience SHALL keep that signal out of the stronger possible-supersession path
