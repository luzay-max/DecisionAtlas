# ADR-0003: Use Citation-First Answering

## Status
Accepted

## Context

The target questions for DecisionAtlas are high-context engineering questions such as “why was this tradeoff made?” and “what changed after this incident?”.

Answers without evidence are not trustworthy enough for that workflow.

## Decision

The answering layer must:

- retrieve supporting evidence first
- generate only over retrieved evidence
- attach source quotes and URLs to every answer
- return an “insufficient evidence” response when support is weak

## Consequences

### Positive

- improves trust
- lowers hallucination risk
- makes review easier

### Negative

- may produce shorter or more conservative answers
- requires better source mapping and retrieval quality

### Neutral

- the product will feel less like a chatbot and more like an evidence assistant

## Alternatives Considered

- Free-form answer generation over raw workspace memory
- Pure search results with no synthesized answer

## References

- [Project Blueprint](../../plans/2026-03-18-decisionatlas-project-blueprint.md)
