## Context

The throughput change improved extraction visibility and reduced wasted work, but a real imported-repository test still ended with:

```text
screened-in artifacts: 47
full extraction requests: 47
created candidates: 0
```

That result is materially different from an import that is merely evidence-limited. It means the system found enough artifact signal to justify full extraction, but the full extraction step itself failed to convert those artifacts into reviewable candidate decisions.

The current full extraction path still has several quality weaknesses:

- one extraction prompt shape is used across very different artifact families
- parser failure remains binary, so partial but decision-like outputs are often discarded
- zero-yield runs are visible numerically, but not yet explained in product terms
- benchmark validation is stronger on throughput than on `screened-in -> candidate` conversion quality

## Goals / Non-Goals

**Goals:**

- Increase the conversion rate from screened-in artifacts to reviewable candidate decisions.
- Make full extraction more robust across docs, PRs, and lighter-weight issue/commit artifacts.
- Preserve conservative behavior without requiring every successful extraction to return a perfect first-pass JSON object.
- Expose actionable diagnostics for low-yield extraction runs so imported workspace outcomes are interpretable.
- Keep the change focused on full extraction quality rather than reopening throughput or retrieval architecture.

**Non-Goals:**

- Redesign shortlist scoring or screening strategy again.
- Redesign why-search retrieval or answer generation.
- Redesign indexing or artifact chunk retrieval.
- Introduce multi-model routing or multimodal extraction infrastructure.
- Replace human review with automatic acceptance logic.

## Decisions

### Decision: Use artifact-family-aware extraction prompts

The system will classify screened-in artifacts into a small set of extraction families, such as:

- rationale-bearing documents
- high-signal PR descriptions
- lighter-weight issue or commit evidence

Each family will use a prompt tuned to the density and style of the source material rather than forcing all artifacts through one generic extraction instruction.

Why:

- architecture and migration docs often contain explicit rationale and long-form context
- PR descriptions often contain implementation choice and tradeoff summaries
- issues and commits often require more permissive handling because the decision signal is narrower

Alternatives considered:

- keep a single prompt and only adjust wording slightly
  - rejected because the failure pattern suggests the current one-size-fits-all prompt is part of the conversion bottleneck
- create a prompt per artifact type with many narrow branches
  - rejected because it creates too much maintenance overhead for a first quality pass

### Decision: Add a candidate salvage path after parsing

The full extraction path will distinguish:

- true “not a decision” outcomes
- malformed/partial structured outputs
- structured outputs with enough core fields to persist a candidate

Instead of treating every malformed or partially structured response as an unrecoverable drop, the system will normalize and salvage outputs when core decision fields are present and source grounding is still adequate.

Why:

- current conversion drops are too binary
- real extraction outputs often fail around formatting or optional-field completeness rather than true absence of decision signal

Alternatives considered:

- keep strict parser rejection and only improve prompts
  - rejected because prompt-only fixes still leave the pipeline brittle
- accept partially structured candidates without normalization
  - rejected because it risks creating noisy review cards

### Decision: Record explicit conversion-loss reasons

The import summary will record why screened-in artifacts failed to become candidates, for example:

- returned null / no decision
- invalid JSON
- missing required fields
- source quote could not be grounded
- provider timeout / request failure

Why:

- the current “0 candidates” outcome is not diagnostic enough
- product and operator decisions should be able to distinguish weak repo evidence from weak extraction conversion

Alternatives considered:

- keep only aggregate created/skipped counts
  - rejected because it does not explain where the conversion loss happened

### Decision: Reflect low-yield extraction in imported workspace outcomes

Imported workspace summaries and readiness surfaces will explain when:

- evidence was strong enough to justify many full extraction attempts
- but conversion into candidates remained low or zero

Why:

- “evidence limited” and “conversion limited” are not the same user story
- the product should avoid implying that the repository lacked signal when the extraction layer is the weaker link

Alternatives considered:

- keep everything under `insufficient_evidence`
  - rejected because it hides an important operational distinction

## Risks / Trade-offs

- **[Risk] More permissive salvage creates noisy candidate decisions** → Mitigation: only salvage when core fields and grounded quotes are present, and validate on benchmark repos.
- **[Risk] Multiple prompt families become harder to maintain** → Mitigation: keep the family set small and tied to stable artifact classes.
- **[Risk] More detailed diagnostics increase summary complexity** → Mitigation: aggregate reasons into compact counters and user-facing outcome labels.
- **[Risk] Conversion improvements may raise candidate count but lower review quality** → Mitigation: track both candidate yield and downstream accepted-decision outcomes during validation.

## Migration Plan

1. Introduce artifact-family-aware prompt selection behind the existing screened-in extraction stage.
2. Add parser normalization and salvage rules while preserving conservative persistence rules.
3. Record conversion-loss counters in extraction summaries and imported workspace read models.
4. Update imported dashboard messaging to explain low-yield extraction separately from low-signal evidence.
5. Validate on curated public repositories, comparing:
   - screened-in count
   - created candidate count
   - accepted candidate count
   - imported workspace readiness outcomes

## Open Questions

- Should salvage permit fallback quote extraction when the model omits a precise `source_quote` but clearly references a grounded section?
- Should low-yield extraction appear as a distinct outcome label, or remain under `insufficient_evidence` with richer detail?
- Which artifact-family split gives the best quality/maintenance tradeoff: `doc / pr / issue+commit`, or a smaller `long-form / short-form` split?
