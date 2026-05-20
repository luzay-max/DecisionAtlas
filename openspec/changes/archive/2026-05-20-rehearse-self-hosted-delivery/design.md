## Context

The project has moved from internal validation toward a self-hosted commercial baseline. Current documentation already describes tiers, deployment prerequisites, readiness checks, release evidence, hosted/operator readiness, benchmark comparison, readiness evidence history, and a Code Decision Audit handoff template.

The remaining gap is operational: these pieces need to be exercised together as one customer-style rehearsal. The rehearsal should prove that an operator can start from the current self-hosted baseline, run the right checks, preserve non-clean states, archive evidence, and produce a customer-readable summary without inventing SaaS features or hiding missing evidence.

## Goals / Non-Goals

**Goals:**

- Define one repeatable self-hosted delivery rehearsal path.
- Produce a dated evidence package that references release evidence, hosted/operator readiness, benchmark comparison, readiness history, and handoff summary artifacts.
- Make `operator_guided`, `warning`, `blocking`, `known_limitation`, and `not_provided` states explicit.
- Use existing scripts and docs where possible instead of adding a new platform surface.
- Prepare a handoff artifact that can support a first paid pilot or private evaluation.

**Non-Goals:**

- Do not add billing, license enforcement, hosted multi-tenancy, Marketplace/self-service OAuth, or hosted secret custody.
- Do not make live external repository or hosted URL availability mandatory for every local rehearsal.
- Do not treat `.tmp` scratch output as durable evidence unless it is explicitly archived.
- Do not claim production SaaS readiness from a local/private self-hosted rehearsal.

## Decisions

1. Use a documentation-first rehearsal contract.

   Existing scripts already generate release evidence, hosted/operator readiness, and readiness history. The change should first define the operator sequence, required evidence families, output paths, and handoff rules. A new service or database model would add complexity before the delivery path is proven.

2. Classify missing live inputs as explicit evidence states.

   Hosted URLs, private repository credentials, provider credentials, and benchmark baselines may be absent in a maintainer-local rehearsal. The rehearsal should record `operator_guided`, `known_limitation`, or `not_provided` rather than failing silently or pretending the lane passed.

3. Archive only selected evidence.

   `.tmp` remains scratch output. Durable release/readiness claims must reference files promoted through readiness evidence history or a customer handoff summary. This keeps accidental secrets, raw private repository data, and local logs out of tracked evidence.

4. Bind the rehearsal to the self-hosted commercial baseline.

   Customer-facing claims should point to a completed rehearsal package or disclose why the package is missing. This prevents the product plan from drifting into marketing-only readiness claims.

## Risks / Trade-offs

- Rehearsal can look successful while key live inputs are absent -> preserve `operator_guided`, `known_limitation`, and `not_provided` states in every summary.
- Evidence artifacts can leak sensitive data -> archive only explicit files and document that secrets, private repository contents, raw model output, and unnecessary local logs are excluded.
- The rehearsal may duplicate release checklist content -> keep the rehearsal as an orchestration/handoff layer that links existing commands instead of redefining each command.
- Too much automation too early may hide operator judgment -> require a customer/operator-readable summary and limitations section.
- Live benchmark or hosted checks may be flaky -> allow a documented substitute or blocker state, but do not convert it into pass.
