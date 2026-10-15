## Context

Governance drift detection currently creates signal IDs from detector-specific inputs and only removes exact duplicate IDs. Repeated postmortem lines can vary by source path, punctuation, timestamps, or generated suffix while representing the same operator action. Those signals propagate unchanged to guardrail summaries, dashboard cards, and release evidence.

The change crosses the engine report model and web-facing contracts, but must preserve existing fields and advisory behavior. Deduplication must not erase independent issues or hide recurrence evidence.

## Goals / Non-Goals

**Goals:**
- Produce one actionable signal per semantic governance issue.
- Preserve and deduplicate all useful source evidence within a bounded limit.
- Expose recurrence metadata additively.
- Keep output deterministic across repeated runs.
- Ensure all downstream consumers receive the canonical result without independent dedupe logic.

**Non-Goals:**
- Automatically resolve, acknowledge, or mutate governance findings.
- Deduplicate persisted workspace drift alerts, which have separate lifecycle and audit semantics.
- Introduce fuzzy embedding similarity or an external search dependency.
- Change advisory severity or CI enforcement policy.

## Decisions

### Canonicalize at the detector boundary

The detector will consolidate signals before it derives report status, human decisions, recommendations, and context counts. This is preferred over dashboard-only filtering because machine consumers and release evidence need the same authoritative result.

Alternative considered: deduplicate in each downstream client. Rejected because it allows CLI, API, dashboard, and evidence to disagree.

### Filter repeated-issue candidates before grouping

Historical issue extraction will use token boundaries, reject explicitly negated outcomes, and require substantial token coverage against recent context. This prevents terms such as decisions, private issue text, and no runtime errors from becoming drift findings.

Alternative considered: group every broad marker match under one UI card. Rejected because it would hide false-positive evidence instead of fixing detector precision.
### Use type-aware deterministic semantic keys

Each signal receives a grouping key from its type plus normalized action-bearing content. For repeated postmortem findings, volatile source prefixes, whitespace, punctuation, counters, and path-specific fragments are removed from the comparison text while meaningful issue wording remains. Other signal types use conservative identity so distinct capabilities, rules, or decisions are not merged accidentally.

Alternative considered: title-only grouping. Rejected because generic titles would over-merge unrelated issues.

### Merge evidence with stable identities and explicit recurrence metadata

Equivalent signals retain the first deterministic representative, merge unique evidence using kind/path/id/title/excerpt identity, and expose additive `occurrence_count` and `source_count` fields. Evidence is sorted and bounded, while counts describe all grouped occurrences even when evidence is truncated.

Alternative considered: retain one signal with no metadata. Rejected because operators need to know whether a finding represents one or many occurrences.

### Preserve API compatibility

Existing signal fields remain unchanged. New integer fields default to one and existing clients can ignore them. Dashboard copy will show recurrence only when the count is greater than one.

### Verify both semantic boundaries

Unit tests will cover normalization, over-merge protection, evidence bounds, ordering, and report status. A real-stack browser rehearsal will verify that the dashboard presents one recurring finding with a recurrence count and that guardrail/release evidence consumes the same canonical count.

## Risks / Trade-offs

- [Normalization merges two genuinely distinct issues] -> Keep keys type-aware and conservative; add near-match non-merge tests.
- [Normalization misses paraphrased duplicates] -> Start deterministic and explainable; record residual duplicate evidence before considering fuzzy matching.
- [Evidence truncation hides a useful source] -> Preserve total source count, deterministic family/path ordering, and a documented bound.
- [Additive fields break strict clients] -> Validate TypeScript schemas and API tests; fields are optional/defaulted in clients during rollout.

## Migration Plan

No database migration is required. Deploy engine and web contracts together, compare before/after signal counts on the current repository, and retain the previous exact-ID deduper as rollback behavior if semantic grouping causes regressions.

## Open Questions

- Whether future operator controls should allow explicit “keep separate” overrides is deferred until real usage shows over-merge cases.
- Fuzzy paraphrase grouping remains deferred pending a labeled benchmark.
