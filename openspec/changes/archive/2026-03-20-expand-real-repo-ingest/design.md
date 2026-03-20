## Context

DecisionAtlas already imports GitHub issues, pull requests, and commits through the remote GitHub API, while markdown and ADR ingestion only exists for local directories. This leaves many real repositories with too little evidence to form meaningful candidate decisions, especially when important rationale lives in `README`, `docs/`, ADRs, RFCs, or release notes rather than in issue threads.

The current product risk is not only low coverage, but low transparency: when a real workspace imports successfully but produces few or no candidates, the user cannot easily tell whether the repository lacked decision evidence, whether the importer skipped useful files, or whether the system failed. This change should improve real-workspace usefulness without widening scope into full source-code analysis, GitHub App auth, or deployment work.

## Goals / Non-Goals

**Goals:**
- Add remote GitHub repository document ingestion for a conservative, high-signal set of markdown files.
- Reuse the existing markdown artifact shape so document evidence flows naturally into indexing, extraction, why search, and drift.
- Expose import transparency so the system can report imported versus skipped document coverage and explain low-signal workspaces.
- Preserve idempotent imports and keep reruns safe for the current import job flow.

**Non-Goals:**
- Import full source trees or perform large-scale source code analysis.
- Add GitHub App installation, private-repo auth changes, or webhook sync.
- Change the citation-first answer contract or redesign extraction prompts in this change.
- Introduce new storage systems or a major artifact model migration.

## Decisions

### 1. Add a remote document selection layer before artifact ingest
The importer should first list repository files, then apply a narrow “high-signal markdown” policy before fetching content. This is preferable to blindly ingesting all repository markdown because many repos contain user docs, generated docs, or reference material that would dilute retrieval quality and increase embedding cost.

Initial include policy:
- top-level `README.md` / `README.mdx`
- top-level decision-oriented markdown such as `ARCHITECTURE.md`, `DECISIONS.md`, `CHANGELOG.md`, `RELEASE_NOTES*.md`, `CONTRIBUTING.md`
- `docs/**/*.md` and `docs/**/*.mdx`
- `**/adr/**/*.md`, `**/adrs/**/*.md`, `**/rfcs/**/*.md`

Initial exclusion policy:
- source files, config files, binaries, generated/vendor directories, lockfiles, and non-markdown content

Alternative considered:
- ingest all markdown files anywhere in the repo
Why not:
- too noisy, too costly, and much harder to explain when retrieval quality drops

### 2. Reuse the existing `doc` artifact type and markdown import semantics
Remote repository documents should land in the same artifact model used by local markdown import, with stable `source_id` values based on repo-relative path and URLs that point to the GitHub blob view. This avoids inventing a second document artifact model and keeps downstream indexing/extraction unchanged.

Alternative considered:
- introduce a new artifact subtype specifically for remote docs
Why not:
- adds branching to indexing and retrieval without meaningful product value at v0.2 scope

### 3. Import jobs should capture document coverage and skip reasons
Import results should distinguish classic GitHub API artifacts from repository documents and report skipped document counts with coarse reasons such as “outside high-signal paths”, “non-markdown”, or “generated/vendor path”. This is necessary so a successful import can still explain why a workspace has low decision coverage.

Alternative considered:
- only return a single imported artifact count
Why not:
- hides too much, especially for repositories that import successfully but do not produce candidates

### 4. Real-workspace empty states should explain evidence scarcity, not imply failure
When a real imported workspace has few or no candidate decisions, the product should surface that the import completed but high-signal decision evidence was limited. This is a product trust decision more than a UI flourish: imported workspaces should look intentionally sparse rather than broken.

Alternative considered:
- leave current generic empty states unchanged
Why not:
- users will continue to misread “no results” as a system failure instead of an evidence limitation

## Risks / Trade-offs

- [Markdown path rules still too wide] → Start with a conservative allowlist and validate on a few public repos before widening coverage.
- [High-signal docs may still be missing in some repos] → Expose import summary and empty-state explanations so sparse results are understandable.
- [Extra GitHub API calls increase latency or rate-limit pressure] → Restrict file discovery to targeted paths and keep existing page caps and token support.
- [Blob URLs may assume the wrong default branch] → Prefer branch-aware URLs if repo metadata is easy to obtain; otherwise document `main` as an initial assumption and revisit if it becomes a common issue.
- [Remote docs may duplicate local/manual imports] → Keep upsert keyed by repo-relative `source_id` and workspace scope so reruns remain idempotent.
