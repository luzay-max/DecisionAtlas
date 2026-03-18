# ADR-0002: Model Decision As The Core Product Object

## Status
Accepted

## Context

DecisionAtlas is not a wiki replacement. Its value depends on restoring engineering intent and making that intent queryable and reviewable over time.

If the system centers documents instead of decisions, it becomes a document browser with AI summarization, not a decision memory system.

## Decision

Use `Decision` as the primary product object.

Supporting objects include:

- `Artifact`
- `SourceRef`
- `Relation`

All generated answers and drift alerts must resolve back through those objects.

## Consequences

### Positive

- supports decision timelines and review workflows naturally
- enables citation-first answers
- provides a stable model for future connectors

### Negative

- extraction quality matters early
- some source material will not map neatly to a decision

### Neutral

- artifacts remain important, but only as supporting evidence

## Alternatives Considered

- Document-centric model
- Chat transcript-centric model

## References

- [Project Blueprint](../../plans/2026-03-18-decisionatlas-project-blueprint.md)
