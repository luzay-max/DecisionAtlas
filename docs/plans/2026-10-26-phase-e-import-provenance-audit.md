# Phase E — imported source capture integrity and provenance audit

**Status:** implementation in review.  
**Base:** \`main@33bc336755999c72c753f08a94806435a821c96e\`, after Phase D / PR #24.  
**Goal:** make the path from GitHub API responses to locally stored evidence auditable without turning metadata into a claim of source authenticity or human acceptance.

## Scope

1. Record a local UTC capture timestamp, capture method, and SHA-256 digest of the exact UTF-8 content stored for each imported GitHub issue, pull request, commit, and selected Markdown document. Keep this in existing \`Artifact.metadata_json\`; no database migration.
2. Preserve allowlisted upstream fields returned by GitHub for issues and pull requests: number, state, update/close timestamps, merge timestamp, merge commit SHA, head SHA and base ref where present. Mark merge state as observed only if the API payload actually contains \`merged_at\`; older/incomplete payloads remain unknown.
3. Compare selected Markdown document bytes with the Git blob SHA returned by the repository tree. If the branch moves between listing and content fetch, fail the import transaction rather than silently storing mismatched content under a mutable branch URL.
4. Extend the operator-approved offline evidence snapshot to show import-time digest status and allowlisted upstream metadata. Compare the import-time digest to the current stored content so post-import mutation is detectable.
5. Keep remote source authenticity \`remote_not_verified\`, semantic support \`not_evaluated\`, independent human review \`not_run\`, and \`automatic_acceptance=false\`. A merged PR is only an observed upstream fact, not proof that the cited decision was adopted.

## Acceptance criteria

- [ ] Mocked GitHub API tests cover merged, unmerged, and missing \`merged_at\` fields.
- [ ] Importer persists a content digest and UTC capture time for every artifact type without leaking credentials.
- [ ] A Markdown tree/content mismatch fails closed and the database transaction can be rolled back.
- [ ] Offline evidence export reports matching, mismatching, and legacy/missing import hashes distinctly.
- [ ] PR merge metadata is propagated only when observed in API payloads; legacy records remain unknown.
- [ ] Existing offline evidence fixtures and the full Windows GitHub Actions CI pass.
- [ ] No live external network calls, private repository data, tokens, LLM calls, database migrations, review-state mutation, or automatic acceptance are introduced in CI.

## Explicitly not completed by CI

This PR tests deterministic behavior using synthetic/local data and mocked API responses. It does **not** claim a successful live GitHub import or prove the authenticity of remote source content. After merge, an operator must run the existing public-import rehearsal against an explicitly authorized public repository, inspect the resulting local import/evidence report, and keep any content-bearing exports outside the repository. Independent reviewer identity and human source review remain a separate gate.

## Next gate after this PR

1. Run a controlled public-repository import rehearsal on an operator-owned local stack.
2. Export only after explicit public-data approval; verify content digests, source URLs, and observed PR merge metadata.
3. Compare a small candidate sample with recorded upstream source captures.
4. Obtain two genuinely independent reviewers before making any human-accuracy or adoption-quality claim.
