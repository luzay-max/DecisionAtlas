## MODIFIED Requirements

### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users can tell whether a real repository run is ready for review, has established an initial accepted-decision baseline, is ready for grounded why usage, is still evidence-limited, is blocked by low-yield extraction conversion, or is better handled by reusing existing workspace state instead of blindly rerunning analysis, SHALL expose that readiness in a richer product-facing form that includes recommended actions and explicit downstream readiness for why and drift, and SHALL reserve `conversion_limited` for runs that still produce no reviewable candidate decisions after the refined candidate-conversion path has been attempted.

#### Scenario: Imported workspace is ready for review
- **WHEN** a live analysis run completes and the imported workspace contains reviewable candidate decisions but no accepted imported decisions yet
- **THEN** the workspace read model SHALL identify that the strongest next action is to review those candidate decisions and establish the first accepted baseline

#### Scenario: Imported workspace establishes a first accepted baseline
- **WHEN** an imported workspace accepts its first imported decision after review
- **THEN** the workspace read model SHALL stop treating the workspace as review-only progress and SHALL surface that an accepted baseline now exists for grounded downstream use

#### Scenario: Imported workspace is evidence-limited
- **WHEN** a live analysis run completes without enough accepted or candidate decisions to support meaningful downstream usage and the run did not show significant screened-in extraction loss
- **THEN** the workspace read model SHALL report that the workspace is evidence-limited and SHALL provide a next-step explanation rather than implying the run is fully ready

#### Scenario: Imported workspace is conversion-limited
- **WHEN** a live analysis run completes after many screened-in or full extraction attempts, the refined conversion path has been exhausted, and the workspace still yields no reviewable candidate decisions
- **THEN** the workspace read model SHALL expose that the workspace is conversion-limited and SHALL explain that extraction quality, not only repository evidence coverage, limited the result

#### Scenario: Existing imported workspace offers reuse actions
- **WHEN** a repository already has an imported workspace with prior import history
- **THEN** the product SHALL be able to present open-existing, incremental-sync, and full-rerun choices rather than forcing another blind full analysis

#### Scenario: Imported workspace is ready for why-search
- **WHEN** an imported workspace has accepted decisions with question-level grounding support
- **THEN** the readiness surface SHALL identify why-search as available and SHALL expose whether drift is also ready, stale, or still unevaluated

#### Scenario: Imported workspace provides bounded recommended actions
- **WHEN** the product renders an imported workspace in dashboard or search
- **THEN** it SHALL be able to use a backend-provided primary next action and secondary recommended actions rather than inventing different local readiness flows

#### Scenario: Improved candidate conversion moves workspace out of conversion-limited
- **WHEN** a repository previously prone to conversion-limited outcomes now produces at least one reviewable candidate through the refined conversion path
- **THEN** the workspace readiness SHALL move to `review_ready` instead of continuing to report `conversion_limited`

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, SHALL distinguish partially supported answers from truly insufficient evidence, SHALL improve retrieval quality for technically equivalent questions, and SHALL use artifact evidence only as a support layer behind the accepted decision anchor, with indexing improvements strengthening that support through better-structured chunk evidence rather than by replacing the accepted-decision trust anchor.

#### Scenario: Imported why-answer is grounded in accepted decisions
- **WHEN** the user asks a why-question in an imported workspace that has accepted decisions and matching source references
- **THEN** the system SHALL answer using those accepted decisions, SHALL identify a primary accepted decision for the answer, and SHALL return citations with the answer

#### Scenario: Imported why-answer has limited support
- **WHEN** the user asks a why-question in an imported workspace, the system selects a primary accepted decision, and only partial but still grounded citation support is available
- **THEN** the system SHALL return an explicit `limited_support` outcome instead of mislabeling the result as fully supported or as completely insufficient

#### Scenario: Truly weak or missing grounding still fails closed after first acceptance
- **WHEN** the user asks a why-question in an imported workspace that has accepted at least one decision but does not yet have enough grounding for the asked rationale thread
- **THEN** the system SHALL continue to return an explicit evidence-limited or review-required outcome instead of upgrading the result solely because the workspace has an accepted baseline

#### Scenario: Imported why-answer keeps related but distinct decisions separate
- **WHEN** the user asks a focused why-question and retrieval also finds nearby but distinct accepted decisions
- **THEN** the system SHALL keep those distinct decisions out of the main answer unless they qualify as supporting context for the same rationale thread

#### Scenario: Imported why-answer can use supporting artifact evidence
- **WHEN** the system finds relevant artifact evidence that supports the already selected primary accepted decision
- **THEN** the imported why experience SHALL use that evidence to strengthen the answer without replacing the primary accepted decision as the answer anchor

#### Scenario: Structured chunk evidence improves imported why support
- **WHEN** improved indexing produces chunk evidence with stronger section context for the same accepted decision rationale thread
- **THEN** the imported why experience SHALL be able to use that structured chunk evidence to improve support quality without changing the accepted decision that anchors the answer

## ADDED Requirements

### Requirement: First accepted imported baseline is treated as a product milestone
The system SHALL treat the first accepted imported decision as the first durable product milestone after candidate review, and SHALL use that milestone to upgrade imported workflow guidance without implying that all downstream questions are now fully supported.

#### Scenario: First accepted milestone changes imported next-step messaging
- **WHEN** an imported workspace transitions from zero accepted decisions to one accepted decision
- **THEN** the product SHALL be able to explain that the workspace now has a durable baseline and can support grounded why usage for matching questions
