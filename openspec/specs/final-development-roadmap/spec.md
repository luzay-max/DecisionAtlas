# final-development-roadmap Specification

## Purpose
Define evidence-backed final roadmap documentation after the self-hosted commercialization and sales enablement work.

## Requirements

### Requirement: Final roadmap reflects current evidence
The roadmap SHALL summarize current project status using current repository evidence.

#### Scenario: Roadmap is reviewed
- **WHEN** a maintainer opens the final roadmap
- **THEN** it MUST identify completed 5.8/5.9 plan lines and cite the current evidence categories that support them

### Requirement: Final roadmap prioritizes remaining work
The roadmap SHALL define the next development sequence after self-hosted commercialization and sales enablement.

#### Scenario: Roadmap is used for planning
- **WHEN** the maintainer chooses the next OpenSpec change
- **THEN** the roadmap MUST list priority, scope, validation, and difficulty for each recommended phase

### Requirement: Final roadmap preserves deferred lanes
The roadmap SHALL explicitly distinguish near-term work from deferred SaaS/commercial infrastructure.

#### Scenario: Deferred capabilities are reviewed
- **WHEN** the roadmap mentions billing, hosted SaaS, Marketplace/OAuth, hosted secret vault, runtime license enforcement, or managed operations
- **THEN** it MUST state that these remain deferred unless a future explicit OpenSpec change changes the route

### Requirement: Roadmap references the completion taskbook
The final development roadmap SHALL reference the current completion taskbook when describing project status and next priorities.

#### Scenario: Roadmap is updated
- **WHEN** a roadmap or master plan is revised after this change
- **THEN** it SHALL distinguish completed evidence, partial evidence, missing evidence, and deferred scope using the taskbook categories.

#### Scenario: Final plan is generated
- **WHEN** a final follow-up development plan is written
- **THEN** it SHALL use the completion taskbook as the source for remaining work rather than duplicating old 2026-05-08 plan items.
