## Purpose
Define expected outcomes and evidence quality for imported real-repository workspaces.
## Requirements
### Requirement: Imported workspaces expose real-analysis readiness
The system SHALL summarize imported-workspace readiness so users and validation operators can tell whether a real repository run is ready for review, has established an initial accepted-decision baseline, is ready for grounded why usage, is still evidence-limited, is blocked by low-yield extraction conversion, has failed operationally, or is better handled by reusing existing workspace state instead of blindly rerunning analysis, SHALL expose that readiness in a richer product-facing form that includes recommended actions and explicit downstream readiness for why and drift, and SHALL reserve `conversion_limited` for runs that still produce no reviewable candidate decisions after the refined candidate-conversion path has been attempted.

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

#### Scenario: Live validation classifies curated repositories into bounded outcomes
- **WHEN** an operator validates a curated public repository through the live real-repo validation flow
- **THEN** the observed outcome SHALL be classified into an explicit state family such as `review_ready`, `why_ready`, `evidence_limited`, `conversion_limited`, `analysis_failed`, `missing_workspace`, or `operational_failure`

#### Scenario: Live validation distinguishes product limitations from operational failures
- **WHEN** live validation cannot complete a why, drift, dashboard, or workspace request because of API availability, provider configuration, network, or missing workspace state
- **THEN** the result SHALL identify the failure as operational rather than presenting it as evidence-limited repository signal

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, SHALL distinguish partially supported answers from truly insufficient evidence, SHALL improve retrieval quality for technically equivalent questions, SHALL use artifact evidence only as a support layer behind the accepted decision anchor, SHALL expose bounded follow-up guidance when an imported workspace has an accepted baseline but the asked why-question is still weakly grounded, and SHALL make retrieval failures diagnosable enough for real-repository validation to classify them.

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

#### Scenario: Accepted baseline with weak why grounding exposes bounded follow-up
- **WHEN** an imported workspace already has an accepted baseline but the asked why-question remains evidence-limited
- **THEN** the response SHALL keep that outcome bounded and SHALL expose follow-up guidance such as reviewing additional candidates or inspecting import evidence instead of implying the baseline alone solved the question

#### Scenario: Equivalent why question records retrieval usefulness
- **WHEN** a real-repository validation why case uses equivalent wording for an accepted imported decision
- **THEN** validation output SHALL be able to record whether the answer selected the expected primary rationale thread and returned the expected bounded support state

### Requirement: Real repository outcomes report decision-value quality
The system SHALL evaluate imported real-repository outcomes not only by readiness state, but also by whether reviewable candidate decisions are valuable, grounded, and useful for establishing the first accepted baseline, using the same candidate quality labels and reason categories exposed in the review product, and SHALL include imported why-search retrieval usefulness when accepted baselines are available.

#### Scenario: Validation records candidate value observations
- **WHEN** an operator validates a curated imported repository
- **THEN** the report SHALL include candidate-quality observations such as reviewable candidate count, strong/partial/thin label distribution, thin-evidence pressure, provenance availability, previewable source-ref availability, and whether a first accepted baseline appears achievable

#### Scenario: Low-value candidates are not treated as equal to strong candidates
- **WHEN** an imported workspace contains candidates with weak grounding or unclear provenance
- **THEN** the product or validation report SHALL distinguish those candidates from strongly grounded candidates instead of treating all candidates as equally review-ready

#### Scenario: First baseline usefulness is recorded
- **WHEN** a reviewer accepts the first imported decision in a real repository workspace
- **THEN** validation output SHALL be able to record whether that baseline unlocks a meaningful why/drift path for matching questions

#### Scenario: Quality report explains thin pressure
- **WHEN** real-repository validation reports a high thin-candidate ratio
- **THEN** the report SHALL expose whether thin pressure is driven by missing source refs, missing previewable quotes, missing provenance, low confidence, or another bounded reason category

#### Scenario: Fixture quality checks remain bounded
- **WHEN** default benchmark fixture validation checks candidate quality
- **THEN** it SHALL use deterministic counts and bounded reason categories rather than live-provider prose or repository-specific hard-coded candidate titles

#### Scenario: Why retrieval quality is recorded after first baseline
- **WHEN** a curated imported repository has an accepted baseline and real-repository why cases
- **THEN** validation output SHALL record expected status, observed status, citation count, expected term matches, and primary-thread match evidence where available

## ADDED Requirements

### Requirement: First accepted imported baseline is treated as a product milestone
The system SHALL treat the first accepted imported decision as the first durable product milestone after candidate review, SHALL make the review path to that milestone clear when imported candidates are available, and SHALL use that milestone to upgrade imported workflow guidance without implying that all downstream questions are now fully supported.

#### Scenario: First accepted milestone changes imported next-step messaging
- **WHEN** an imported workspace transitions from zero accepted decisions to one accepted decision
- **THEN** the product SHALL be able to explain that the workspace now has a durable baseline and can support grounded why usage for matching questions

#### Scenario: Review queue explains milestone before first acceptance
- **WHEN** an imported workspace has reviewable candidate decisions and no accepted imported decision
- **THEN** the review experience SHALL explain that accepting a well-supported candidate establishes the first baseline for downstream why/drift usage

#### Scenario: Review acceptance does not overstate downstream trust
- **WHEN** the first imported candidate is accepted
- **THEN** downstream guidance SHALL still distinguish grounded matching why questions from unrelated questions that remain review-required or evidence-limited

### Requirement: Curated real-repository validation classifies product value
The system SHALL classify curated real-repository benchmark outcomes so validation reports can distinguish useful product behavior, bounded product limitations, and operational blockers.

#### Scenario: Repository is useful now
- **WHEN** a curated imported repository has reviewable or accepted decisions, acceptable candidate quality, and focused why or drift cases that meet their bounded expectations
- **THEN** validation output SHALL classify the repository as useful for the benchmarked DecisionAtlas workflow

#### Scenario: Repository is reviewable but limited
- **WHEN** a curated imported repository has reviewable candidates but weak grounding, thin-candidate pressure, missing provenance, or limited downstream why/drift usefulness
- **THEN** validation output SHALL classify the repository as reviewable with explicit limitations rather than treating it as fully successful or failed

#### Scenario: Repository is conversion or evidence limited
- **WHEN** a curated imported repository produces enough import evidence to analyze but cannot produce useful reviewable decisions or downstream support
- **THEN** validation output SHALL classify the limitation as conversion-limited or evidence-limited with bounded supporting metrics

#### Scenario: Repository is operationally blocked
- **WHEN** validation cannot evaluate a curated repository because of missing workspace state, API availability, provider configuration, GitHub/network failure, or another setup issue
- **THEN** validation output SHALL classify the result as missing-workspace or operationally blocked rather than as product evidence

#### Scenario: Value classification remains benchmark-only
- **WHEN** value classification is computed for curated real-repository validation
- **THEN** the classification SHALL remain part of benchmark/reporting behavior and SHALL NOT introduce repository-specific product runtime behavior
