## Context

DecisionAtlas already has three related building blocks:

- Markdown governance ingest stores human-authored standards, roadmaps, postmortems, and accepted rule drafts.
- Governance diff checker evaluates the current workspace diff against active OpenSpec context, roadmap references, main specs, accepted rules, and validation expectations.
- Workspace drift evaluation compares accepted decisions against later imported artifacts.

Stage 6 should connect these ideas without turning the system into an automatic authority. The first implementation should report long-term governance drift signals across project artifacts and make the evidence explicit enough for a human or future AI agent to review.

## Goals / Non-Goals

**Goals:**

- Produce a local governance drift report that looks across roadmap, specs, archived changes, accepted governance rules, update logs, postmortems, and optional current diff context.
- Classify signals such as `roadmap_mismatch`, `spec_gap`, `stale_rule`, `repeated_postmortem_issue`, and `unsynced_decision`.
- Return machine-readable output with status, evidence references, human decision points, and recommended next actions.
- Reuse existing governance and OpenSpec context conventions where practical.
- Keep the result advisory and explainable.

**Non-Goals:**

- Do not persist drift reports in the database in the first version.
- Do not add UI or API routes in the first version unless implementation reveals a small wrapper is necessary.
- Do not automatically update specs, accepted rules, roadmap documents, or code.
- Do not make the report a default CI blocker.
- Do not rely on opaque LLM-only judgment for first-version status.

## Decisions

### Decision 1: Add a separate governance drift report entrypoint

Create a new local module and script adjacent to the existing governance diff checker rather than extending the diff checker directly.

Rationale:

- The diff checker answers whether the current change is acceptable.
- Drift detection answers whether governance knowledge is becoming inconsistent over time.
- Keeping them separate avoids mixing single-change validation with longitudinal project analysis.

Alternative considered: add more modes to the existing diff checker. This was rejected because the result schema and mental model would become overloaded.

### Decision 2: Use deterministic signal detectors first

The first report should use deterministic heuristics and bounded evidence extraction:

- roadmap plan references
- main OpenSpec specs
- archived OpenSpec proposal/design/tasks/spec deltas
- governance documents and accepted rules
- update logs and postmortem-like documents
- optional current diff paths and text

Rationale:

- Deterministic signals are testable and safe to run without provider credentials.
- Future AI agent use needs stable evidence objects before interpretation can become more advanced.

Alternative considered: use an LLM to summarize all drift immediately. This was rejected for the first version because it would be harder to validate and could overstate uncertain drift.

### Decision 3: Report signal severity conservatively

Use a status model such as `clean`, `watch`, `drift_detected`, and `review_required`, with individual signals carrying `note`, `warning`, or `blocker` severity.

Rationale:

- Most governance drift is ambiguous and should request human review rather than claim certainty.
- Blockers should be reserved for hard conflicts with accepted blocker rules or missing governance synchronization that directly contradicts active rules.

Alternative considered: reuse `pass`, `warning`, and `blocked` from the diff checker. This was rejected because long-term drift is better framed as report status rather than merge readiness.

### Decision 4: Keep evidence as the primary product surface

Every drift signal should include source references such as file path, document title, rule id, archived change name, excerpt, and signal reason.

Rationale:

- The report must be auditable.
- Future AI agents can use the evidence list as grounded context.
- Human reviewers can decide whether to update specs, mark a rule superseded, accept a new rule, or revise roadmap.

Alternative considered: emit only a summary and recommendations. This was rejected because it would make the report hard to trust.

## Risks / Trade-offs

- [Risk] Drift detection becomes noisy because roadmap and update logs use broad language. → Mitigation: first-version signals should favor `watch` and `warning` over blockers, with short bounded excerpts.
- [Risk] The report duplicates existing workspace drift alerts. → Mitigation: keep scope focused on governance artifacts, not accepted product decisions inside a workspace.
- [Risk] Users treat advisory output as automatic truth. → Mitigation: documentation and schema must call out advisory-only behavior and human decision points.
- [Risk] Historical documents may be stale or contradictory. → Mitigation: document status and accepted rule state should be respected; deprecated or superseded sources should produce stale-rule signals rather than hard enforcement.
- [Risk] The first version misses subtle semantic drift. → Mitigation: design for future AI interpretation, but start with deterministic evidence and fixtures.

## Migration Plan

No database migration is expected for the first version.

Implementation sequence:

1. Add local report schema and context collectors.
2. Add deterministic signal detectors.
3. Add CLI wrapper and JSON output.
4. Add fixtures and tests.
5. Add documentation and validation commands.

Rollback is simple: remove the new local script/module and docs. Existing governance ingest, diff checker, and workspace drift evaluation remain independent.

## Open Questions

- Should the first report include only repository files, or also accepted governance rules from the configured local database when available?
- Should archived OpenSpec changes be scanned by default, or bounded by recent count/date to avoid noisy historical reports?
- Should the first version output a markdown summary in addition to JSON, or keep markdown as a later formatter?
