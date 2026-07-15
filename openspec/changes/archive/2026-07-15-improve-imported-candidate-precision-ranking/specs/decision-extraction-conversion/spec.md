## ADDED Requirements

### Requirement: Created candidates retain bounded extraction provenance
The extraction conversion path SHALL persist bounded per-candidate provenance that identifies artifact family, parser salvage, and recovery path without retaining raw provider responses.

#### Scenario: Normal extraction creates candidate metadata
- **WHEN** a normal full-extraction attempt creates a candidate
- **THEN** the candidate SHALL retain its artifact family and explicit non-recovery extraction state

#### Scenario: Salvaged output remains attributable
- **WHEN** parser salvage produces a structurally valid grounded candidate
- **THEN** that candidate SHALL retain a parser-salvaged marker for review ranking and diagnostics

#### Scenario: Recovery output remains attributable
- **WHEN** bounded recovery or sparse recovery creates a candidate
- **THEN** that candidate SHALL retain the applicable recovery markers and final artifact family

#### Scenario: Raw provider output is excluded
- **WHEN** candidate extraction provenance is persisted
- **THEN** it SHALL contain only allowlisted bounded fields and SHALL NOT contain raw model responses, prompts, credentials, or repository source content
