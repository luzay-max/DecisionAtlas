## Context

Stage 4 added the governance knowledge substrate: Markdown governance documents can be imported, deterministic rule drafts can be reviewed, and accepted governance rules can be stored with source traceability. Stage 5 should make that knowledge useful during development by checking the current git diff against project direction before a change is merged.

The project already uses OpenSpec changes, main specs, roadmap documents, update logs, accepted decisions, and accepted governance rules. The checker should read these artifacts and return a conservative, explainable result. It should not become an autonomous judge that rewrites rules, blocks CI by default, or replaces human review.

## Goals / Non-Goals

**Goals:**

- Add a local governance check path for the current git diff.
- Assemble bounded context from git diff, OpenSpec, roadmap, specs, accepted governance rules, and recent project logs.
- Return a structured result suitable for humans and later AI agent calls.
- Detect high-value early failures such as missing OpenSpec change, roadmap mismatch, accepted-rule conflict, missing tests, and weak validation evidence.
- Keep findings source-linked so users can inspect which spec, roadmap line, or accepted rule caused a warning.

**Non-Goals:**

- No automatic code modification.
- No automatic governance rule rewriting.
- No default CI blocking.
- No free-form AI verdict as the only result.
- No full compliance platform or multi-project enterprise policy engine.

## Decisions

### Decision: Start with a local deterministic checker

The first implementation should run locally against the current workspace and produce deterministic findings wherever possible. This keeps the feature testable and prevents provider credentials from becoming a requirement for basic governance checks.

Alternative considered: implement an LLM-first reviewer immediately. That could produce richer language, but it would make validation harder and would risk presenting soft judgments as hard project truth too early.

### Decision: Use a structured result schema

The checker should return a stable object with `status`, `findings`, `matched_rules`, `conflicts`, `required_tests`, and `recommended_next_action`. This lets the result be rendered in CLI, API, UI, or consumed by an AI agent later without changing the core contract.

Alternative considered: print only human-readable text. That is easier initially, but it makes later AI/tool integration brittle.

### Decision: Treat blocker as a bounded category

`blocked` should be reserved for concrete governance failures such as missing required OpenSpec context for non-trivial code changes or direct contradiction with accepted governance rules. Ambiguous alignment concerns should remain `warning`.

Alternative considered: aggressively block on all uncertainty. That would create noise and reduce trust in the checker.

### Decision: Use accepted governance rules as trust anchors

The checker should only treat accepted governance rules as enforceable context. Pending or rejected rule drafts can be mentioned as non-authoritative context only if explicitly useful, but they must not drive blocker findings.

Alternative considered: use every imported governance document as policy. That would undermine the Stage 4 human-review boundary.

## Risks / Trade-offs

- False positives from simple matching -> keep findings source-linked and downgrade ambiguous cases to warning.
- Missing nuanced project direction -> allow roadmap/spec references and later optional AI explanation as an enhancement.
- Checker becoming a hidden release gate -> document that it is advisory unless a future change explicitly wires it into CI.
- Context overload from large diffs/specs -> collect bounded summaries and cap source excerpts.

## Migration Plan

- Add checker data structures and a local command/script entrypoint.
- Add context collectors for git diff, OpenSpec, specs, roadmap, accepted governance rules, and update logs.
- Add deterministic evaluators for missing OpenSpec, rule conflict, roadmap mismatch, and validation/test expectation gaps.
- Add fixtures and tests for each status bucket.
- Document how to run the checker and how to interpret results.

Rollback is straightforward because the first slice does not alter database schema or runtime product behavior unless explicitly invoked.

## Open Questions

- Should the first user-facing entrypoint be a Python module, a Node script, or both wrapped by a single package command?
- Should accepted governance rules be read directly from the engine database, exported JSON, or API for the first local implementation?
- Should the first UI surface wait until the local checker result schema has stabilized?
