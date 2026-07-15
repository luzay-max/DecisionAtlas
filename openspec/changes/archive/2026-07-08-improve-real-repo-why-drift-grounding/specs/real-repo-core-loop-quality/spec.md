## ADDED Requirements

### Requirement: Why and drift warnings are grounded
The system SHALL attach bounded grounding metadata to product-controlled `why_search` and `drift` warning lanes in real repository core-loop diagnosis.

#### Scenario: Why-search warning remains product-controlled
- **WHEN** a real repository diagnosis reports a `why_search` warning for a repository whose setup is complete
- **THEN** the diagnosis SHALL include a compact reason code and release-readable summary explaining whether the gap is weak why-answer support, missing accepted-decision evidence, or unknown grounding.

#### Scenario: Drift warning remains product-controlled
- **WHEN** a real repository diagnosis reports a `drift` warning for a repository whose setup is complete
- **THEN** the diagnosis SHALL include a compact reason code and release-readable summary explaining whether the gap is unresolved drift follow-up, stale/superseded evidence, missing accepted-decision evidence, or unknown grounding.

### Requirement: Grounding details flow into release evidence
The system SHALL preserve why/drift grounding details through multi-repo diagnosis and warning-lane reduction outputs.

#### Scenario: Multi-repo Markdown is generated
- **WHEN** multi-repo live diagnosis writes Markdown for repositories with `why_search` or `drift` warnings
- **THEN** the Markdown SHALL show compact grounding details without embedding secrets, raw private source, or raw model output.

#### Scenario: Warning-lane reduction is generated
- **WHEN** random repo warning-lane reduction classifies a product-controlled repository lane
- **THEN** the classified lane SHALL include compact grounding details for the product-controlled why/drift warnings so the next remediation is actionable.
