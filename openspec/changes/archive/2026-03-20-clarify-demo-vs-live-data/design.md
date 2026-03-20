## Context

DecisionAtlas currently uses two different data sources in the same product flow:

- seeded demo data created by local preparation scripts to guarantee a stable walkthrough
- real imported repository data fetched from GitHub and processed by the engine

The current UI and API contracts do not distinguish these sources. Dashboard, why search, timeline, drift, and decision detail can therefore present seeded content with the same framing as imported content. This is a cross-cutting problem because it touches backend serialization, frontend typing, shared page copy, and the mental model of the public demo.

The repository does not yet have an existing OpenSpec capability for provenance or workspace mode, so this change introduces a new capability. The design must improve trust without expanding scope into importer quality, hosted deployment, or auth.

## Goals / Non-Goals

**Goals:**
- Introduce a workspace-level provenance model that classifies a workspace as `demo`, `imported`, or `mixed`.
- Expose provenance summary information through read APIs used by dashboard, why search, timeline, drift, and decision detail.
- Update the main demo pages so users can tell whether they are looking at seeded demo data or imported repository data.
- Keep the first iteration small enough to implement without redesigning every database entity.

**Non-Goals:**
- Expanding GitHub import coverage or improving extraction quality.
- Introducing entity-level provenance for every artifact, decision, and alert in the schema.
- Changing provider behavior, hosted deployment, auth, or private repository support.
- Rewriting the current demo seeding model.

## Decisions

### 1. Use workspace-level provenance as the first implementation boundary

The first version will classify the workspace as:

- `demo`: seeded walkthrough workspace with no imported data requirement
- `imported`: workspace whose visible content is derived from imported repository data
- `mixed`: workspace containing both seeded baseline content and imported content

Why:

- This solves the immediate trust problem with low surface area.
- It avoids a large schema migration across every entity type.
- The main user confusion is about what kind of workspace they are viewing, not yet about per-record forensic lineage.

Alternative considered:

- Full entity-level provenance now. Rejected for v1 because it would broaden the change into a metadata redesign and slow delivery.

### 2. Compute provenance in backend API responses instead of persisting a new database column first

The initial implementation should derive provenance in backend serializers and response builders using known workspace characteristics and source patterns.

Why:

- It keeps the migration burden low.
- It allows the team to validate the provenance model in product copy before locking it into schema.
- It can still be promoted to persistent schema later if the model proves stable.

Alternative considered:

- Add a `workspace_mode` column immediately. Rejected for the first pass because the product still needs to validate exact semantics for `mixed`.

### 3. Add explicit provenance fields to user-facing read responses

The APIs supporting dashboard and explanation flows should return explicit provenance data such as:

- `workspace_mode`
- `source_summary`
- optional page-specific context like `answer_context` or `timeline_context`

Why:

- Frontend should not infer provenance from slug naming or repo URL.
- Shared typed fields reduce future ambiguity.
- This keeps provenance language consistent across pages.

Alternative considered:

- Hardcode labels in frontend by checking `demo-workspace`. Rejected because it is brittle and does not scale to multiple demo or imported workspaces.

### 4. Apply provenance labeling only to the main user trust surfaces in this change

The mandatory surfaces in scope are:

- dashboard
- why search
- timeline
- drift
- decision detail
- homepage/demo-facing explanatory copy

Why:

- These are the places where users most easily misread seed data as live repository analysis.
- This keeps the implementation aligned with the proposal instead of broadening into every page.

Alternative considered:

- Label every page and every card in the product. Rejected because the first win is page-level clarity, not exhaustive labeling.

### 5. Keep messaging explicit and product-facing

Labels should not use internal engineering jargon alone. They should say things like:

- `Demo Workspace`
- `Imported Workspace`
- `Mixed Workspace`
- `This answer is based on seeded demo evidence`
- `This timeline reflects imported accepted decisions`

Why:

- The goal is user trust, not internal metadata exposure.
- Product language should explain the meaning, not just expose a raw enum.

Alternative considered:

- Display only raw provenance enums. Rejected because it pushes interpretation burden onto the user.

## Risks / Trade-offs

- [Derived provenance logic becomes fragile] -> Keep the first rules simple and document them clearly in code and tests.
- [Mixed mode semantics are unclear] -> Treat `mixed` as an allowed but conservative state, and keep product copy explicit instead of pretending it is clean.
- [The change drifts into a large data-model redesign] -> Explicitly limit v1 to workspace-level provenance and page-level labeling.
- [Users may still over-trust seeded answers] -> Add provenance context directly near why answers, timeline headers, and drift summaries rather than only on the dashboard.
- [API changes ripple through multiple frontend types] -> Add typed provenance fields in one shared frontend API module and update all affected pages together.

## Migration Plan

1. Extend backend read responses with workspace provenance fields.
2. Update frontend API types to include those fields.
3. Update dashboard, why search, timeline, drift, decision detail, and homepage copy to consume provenance context.
4. Add tests covering demo and imported workspace labeling behavior.
5. Roll forward without database migration in the first pass.

Rollback strategy:

- Revert the API field additions and remove frontend provenance UI if the copy or derived logic proves misleading.
- Because this version is response-layer driven, rollback should not require data migration.

## Open Questions

- Should `decision detail` show only workspace-level provenance or also decision-level provenance hints?
- How should `mixed` be detected in the first version: by seed artifact markers, workspace slug conventions, or a dedicated computed rule set?
- Should why-search responses include counts such as number of imported decisions or source refs used in the answer context?
