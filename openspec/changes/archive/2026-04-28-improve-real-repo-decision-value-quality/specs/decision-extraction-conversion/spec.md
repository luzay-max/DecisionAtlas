## ADDED Requirements

### Requirement: Conversion diagnostics distinguish valid output from valuable candidate
The extraction conversion path SHALL distinguish candidates that are structurally valid from candidates that are valuable enough to serve as imported review baseline candidates.

#### Scenario: Structurally valid but low-value candidate is diagnosable
- **WHEN** extraction creates a candidate with weak decision specificity, thin grounding, or unclear provenance
- **THEN** diagnostics SHALL preserve enough context for review and validation surfaces to label the candidate as low-value or thin rather than silently treating it as strong

#### Scenario: Strong converted candidate preserves reviewer context
- **WHEN** extraction creates a candidate with clear decision content and grounded source refs
- **THEN** conversion output SHALL preserve enough artifact and source-ref context for the review card to show why it is a good baseline candidate

#### Scenario: Quality diagnostics remain bounded
- **WHEN** conversion diagnostics are generated
- **THEN** they SHALL use bounded categories and counters rather than raw provider prose or repository-specific hard-coded labels
