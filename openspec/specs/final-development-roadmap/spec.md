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
