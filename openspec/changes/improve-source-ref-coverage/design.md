## Context

Imported why-search now has better focus and support grading, but recent live validation shows that correct accepted decisions often expose only one grounded source reference. This leaves many answers in `limited_support` even when the right decision has clearly been found.

The bottleneck is no longer primarily retrieval. It is upstream grounding density:

- extraction can create a valid decision
- the decision detail may still retain only one usable quote/span
- downstream why-search therefore cannot satisfy the stronger `ok` threshold

This change is cross-cutting because it touches extraction output handling, source-ref persistence, and downstream quality benchmarks. It should improve support density without weakening trust boundaries or inflating ungrounded quotes.

## Goals / Non-Goals

**Goals:**
- Increase the number of accepted/imported decisions that retain two or more grounded source references when the artifact evidence supports them.
- Preserve conservative grounding: additional source refs must still map back to real artifact spans.
- Make thin-coverage failures more visible so future tuning is based on measured grounding loss instead of guesswork.
- Improve the share of imported why answers that can move from `limited_support` to `ok`.

**Non-Goals:**
- Rework why retrieval or primary-decision selection.
- Loosen support grading thresholds.
- Change workspace reuse, drift behavior, or user/account semantics.
- Treat approximate or guessed quotes as grounded evidence.

## Decisions

### Decision: Improve coverage inside extraction/grounding rather than relaxing why thresholds

The system should improve upstream source-ref density instead of weakening the meaning of a fully supported why-answer.

Why:
- `ok` should continue to mean strongly grounded
- the current issue is missing supporting refs, not overly strict primary-decision selection

Alternatives considered:
- lower the `ok` threshold from two citations to one
  - rejected because it would collapse `limited_support` and weaken trust semantics
- infer additional support in the UI
  - rejected because grounding is a backend evidence decision

### Decision: Prefer multiple grounded refs from the same artifact before broadening to more artifacts

When a decision is extracted from a strong artifact, the first improvement should be recovering more than one grounded ref from that same artifact if the text supports it.

Why:
- same-artifact multi-quote coverage is easier to reason about
- it avoids broadening into loosely related artifacts just to satisfy a citation count

Alternatives considered:
- aggressively pull additional refs from neighboring artifacts
  - rejected because it raises the risk of weak or topic-adjacent support masquerading as direct grounding

### Decision: Track grounding-loss explicitly

The system should record when a decision was created successfully but failed to accumulate enough grounded refs.

Why:
- today many answers stop at `limited_support`, but the system does not clearly distinguish “valid decision, thin refs” from broader extraction failure
- this makes future tuning harder

Alternatives considered:
- rely only on why-answer outcomes
  - rejected because why results are downstream symptoms, not direct grounding diagnostics

## Risks / Trade-offs

- **[Risk] higher recall introduces weak refs** → Mitigation: only persist refs that map back to concrete artifact spans and keep exact grounding checks.
- **[Risk] same-artifact multi-quote extraction still leaves some decisions thin** → Mitigation: record thin-coverage diagnostics so later work can target cross-artifact support only where needed.
- **[Risk] extraction complexity grows faster than measured gain** → Mitigation: validate with imported why cases and track whether `limited_support` meaningfully converts to `ok`.
- **[Risk] more refs clutter decision detail** → Mitigation: cap visible refs and keep UI summarization separate from storage density.

## Migration Plan

1. Improve extraction/parser/source-ref persistence to retain multiple grounded refs when available.
2. Record thin-coverage diagnostics in extraction or why validation outputs.
3. Re-run imported why validation against known one-citation cases.
4. Confirm more cases move from `limited_support` to `ok` without increasing ungrounded refs.

Rollback is straightforward:

- revert to the prior source-ref creation path
- keep `limited_support` grading intact
- no database migration is required if stored refs remain schema-compatible

## Open Questions

- Should the first version support only multiple refs from the same artifact, or also look for secondary grounded refs across additional supporting artifacts?
- Where is the most stable boundary for “thin coverage” diagnostics: extraction summary, decision detail, or why evaluation logs?
- Should source-ref ordering prefer quote diversity (problem + choice + tradeoff) over simple relevance score ranking?
