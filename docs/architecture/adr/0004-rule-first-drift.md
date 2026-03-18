# ADR-0004: Start Drift Detection With Rules Before Semantic Classification

## Status
Accepted

## Context

Drift detection is a key differentiator, but it is also the easiest place to over-promise with noisy semantics.

The MVP needs drift detection that is explainable, testable, and safe to demo.

## Decision

Implement drift detection in two layers:

1. rule-first evaluation over explicit constraints
2. semantic enrichment after the rule layer is stable

The UI must label early alerts conservatively, such as `possible_drift` and `needs_review`.

## Consequences

### Positive

- improves explainability
- keeps false positives more manageable
- creates a clear path for iterative enrichment

### Negative

- first-pass coverage will be narrow
- semantic detection arrives later

### Neutral

- rules can be extracted from accepted decisions as the review set grows

## Alternatives Considered

- Semantic-only drift detection from day one
- No drift detection in MVP

## References

- [Implementation Plan](../../plans/2026-03-18-decisionatlas-implementation-plan.md)
