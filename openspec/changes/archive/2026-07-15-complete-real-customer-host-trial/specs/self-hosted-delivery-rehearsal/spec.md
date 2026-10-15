## MODIFIED Requirements

### Requirement: Delivery rehearsal references external install evidence
The self-hosted delivery rehearsal SHALL include the customer-host trial operator kit and external install evidence before claiming customer-controlled host install readiness.

#### Scenario: External install evidence is available
- **WHEN** a self-hosted delivery rehearsal claims customer-controlled host install readiness
- **THEN** the rehearsal summary SHALL reference the operator kit version, external install evidence JSON or Markdown, external host class, package identity, core lane statuses, blockers, proof level, and limitations

#### Scenario: External install evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without external install evidence
- **THEN** the rehearsal SHALL classify customer-controlled host install readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that the package has been validated on a non-developer or customer-controlled machine.

### Requirement: Delivery rehearsal includes customer-host trial execution guidance
The self-hosted delivery rehearsal SHALL provide an ordered command sequence for an operator to run the customer-host trial kit and archive its result.

#### Scenario: Operator prepares an external trial
- **WHEN** an operator starts a customer-host trial
- **THEN** the rehearsal guidance SHALL identify the sanitized input template, package/version identity, startup and health commands, core browser workflow, continuity evidence, and archive command.

#### Scenario: Trial runs only on local infrastructure
- **WHEN** an operator can validate only a local workstation or local Docker environment
- **THEN** the rehearsal SHALL label the result `operator_guided` or `known_limitation`
- **AND** SHALL NOT present it as external customer-host proof.
