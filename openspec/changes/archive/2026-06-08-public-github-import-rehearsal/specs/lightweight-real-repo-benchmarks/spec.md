## ADDED Requirements

### Requirement: Live benchmark evidence distinguishes import setup from product result
Live real-repository benchmark evidence SHALL distinguish selected-but-not-imported repositories, successfully imported repositories, and imported repositories with product-quality limitations.

#### Scenario: Selected repository is not imported
- **WHEN** live benchmark validation targets a curated repository whose expected workspace is missing
- **THEN** the benchmark report SHALL classify the result as missing-workspace/operator-setup evidence and SHALL NOT count it as a product benchmark pass

#### Scenario: Repository is imported before benchmark
- **WHEN** live benchmark validation targets a curated repository whose expected workspace exists after public import rehearsal
- **THEN** the benchmark report SHALL evaluate the workspace as product evidence and include bounded readiness, candidate, why, drift, limitation, and follow-up fields

#### Scenario: Imported workspace has weak product evidence
- **WHEN** the imported workspace exists but benchmark observations show thin candidates, weak why support, drift limitations, or insufficient accepted baseline
- **THEN** the benchmark report SHALL classify those as product limitations or follow-up categories rather than operator setup failures
