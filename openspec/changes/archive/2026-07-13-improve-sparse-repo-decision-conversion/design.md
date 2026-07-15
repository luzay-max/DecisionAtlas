## Context

The current import pipeline already shortlists artifacts, screens decision likeness, requests full extraction, retries invalid extraction with a focused recovery prompt, validates quotes, and creates review-state candidates. The fresh `sniffio` run showed a narrower gap: one artifact was screened in and extracted, but the model returned `null_decision`; no bounded second look across the remaining high-signal evidence was available, leaving the workspace with no reviewable baseline.

The solution must improve recall without weakening grounding, allowing unbounded model spend, accepting decisions automatically, or turning sparse evidence into fabricated decisions.

## Goals / Non-Goals

**Goals:**

- Detect the specific sparse-conversion state: successful import, zero candidates, and remaining eligible high-signal evidence.
- Run a deterministic, small second-stage selection across evidence families that were not fully extracted.
- Use a recovery prompt that asks for a candidate only when explicit problem, choice, rationale/trade-off, and source quote are present.
- Reuse existing candidate parsing, quote validation, source-ref creation, confidence limits, and human review state.
- Emit counters and reason codes that make improved yield and residual loss comparable in live rehearsals.

**Non-Goals:**

- Automatically accept, approve, or promote recovered candidates.
- Infer decisions from repository popularity, code shape, commit metadata alone, or unsupported model knowledge.
- Reprocess every artifact, increase the normal shortlist without bounds, or hide provider failures.
- Guarantee that every repository produces a candidate.

## Decisions

### 1. Trigger recovery only for an evidence-backed zero-candidate state

Recovery runs only after the normal extraction phase completes with zero created candidates, at least one imported artifact remains eligible, and the configured sparse-recovery budget is positive. This avoids changing successful imports and prevents ordinary low-signal repositories from creating artificial candidates.

Alternative considered: always enlarge the first-pass shortlist. Rejected because it raises cost for every repository and makes baseline comparisons harder.

### 2. Select a bounded, family-diverse recovery set

The recovery selector ranks remaining artifacts using existing signal metadata and explicit decision-language cues, then chooses a small deterministic set across PR, commit, issue, and document families. Previously fully extracted artifacts are excluded unless their only outcome was `null_decision` and they still contain explicit decision evidence.

Alternative considered: retry only the first null result. Rejected because sparse repositories often distribute context and rationale across different artifact families.

### 3. Preserve existing grounding and review boundaries

Recovered output passes through the same parser, required-field validation, source quote matching, source-reference persistence, confidence handling, and candidate review state as normal extraction. A recovery-specific prompt can improve focus, but it cannot bypass these gates. Recovered decisions remain `candidate`.

Alternative considered: synthesize a candidate from multiple artifacts before review. Deferred because cross-artifact synthesis needs a stronger provenance model.

### 4. Make conversion outcomes first-class evidence

Import summaries record whether sparse recovery was eligible, attempted, skipped, or exhausted; the number and family of selected artifacts; model attempts; recovered candidates; rejected outputs; and reason codes such as `no_eligible_evidence`, `null_decision`, `ungrounded_quote`, and `provider_failure`. Fresh-import evidence copies these compact metrics and preserves zero-candidate outcomes.

### 5. Validate with deterministic fixtures before live repositories

Unit tests cover triggering, non-triggering, deterministic family selection, budget limits, grounded candidate creation, invalid quote rejection, provider failure, and summary counters. The live gate uses a previously unused public repository and compares import/candidate results without auto-review.

## Risks / Trade-offs

- [Higher model cost on sparse repositories] → Keep a separate small recovery budget and expose attempt counts.
- [False-positive candidates] → Require explicit choice/rationale evidence, existing quote matching, and human review.
- [Repository-specific overfitting] → Use family-diverse fixtures and at least two real repository profiles over time.
- [Provider nondeterminism] → Treat live candidate yield as evidence, not a deterministic unit-test assertion; preserve model/provider metadata only in sanitized form.
- [Zero candidates remain possible] → Report `evidence_limited` with reason codes rather than claiming failure or fabricating a baseline.

## Migration Plan

No database migration or public API break is required. Add the bounded selector and summary fields behind conservative defaults, run focused engine tests, then execute a fresh real-repository rehearsal. Rollback removes the recovery invocation while leaving additive summary fields harmless.

## Open Questions

- Whether a future iteration should support cross-artifact synthesis with multiple source refs.
- Whether recovery budgets should become operator-configurable after real-repository benchmark data is sufficient.
