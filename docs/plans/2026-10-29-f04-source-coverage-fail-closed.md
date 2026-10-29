# F04 — Fail closed on incomplete GitHub source coverage

**Date:** 2026-10-29
**Base:** `main@8aa461f5bc30f16e023c9c00f0d641794fd16f86`
**Status:** Draft PR for CI review; NOT merge-approved.

## Problem

- `GitHubClient._paginate` formerly returned a truncated list after `max_pages` or HTTP 422 on a later page while the previous page linked onward.
- `list_repository_files` formerly ignored `truncated: true` from Git Tree API.
- The UI/job could then report a complete successful import when source history or repo document enumeration was incomplete.

## Conservative first-step fix

- Raise `GitHubIncompleteCoverageError` (reason: `page_limit`, `pagination_rejected`, `tree_truncated`, or `invalid_page_limit`) before any result is claimed complete.
- Record `incomplete_source_coverage` as the job failure category. Include source endpoint, number of records or repository ref, and reason in the failure message.
- Retain the configured `max_pages` bound and existing public/private access policy. A page without `rel=next` is considered completed normally, including a full 100-item last page.
- The GitHub importer fetches issue/PR/commit listing and tree *before* upserting artifacts, so these conditions abort before writing new artifacts. Jobs are not marked successful; no false incremental watermark is advanced.

## Explicit trade-off

This is **fail-closed**, not "partial-import succeeded". Large repositories with >`max_pages` may now fail an import that previously succeeded with unreported partial coverage. Do not increase the page limit without resource-budget review. Later work can add a separate bounded preview/partial outcome and explicit coverage metadata for UI/Why/MCP. This PR does not claim complete fidelity for Github API results beyond its reported coverage checks.

## Automated acceptance
- [ ] HTTP 422 on later page raises `pagination_rejected` rather than returning partial records.
- [ ] Continuing `rel=next` after configured limit raises `page_limit`, without fetching beyond limit.
- [ ] Truncated Git tree raises `tree_truncated` without pretending full tree listing.
- [ ] Clean no-next page and complete tree still succeed.
- [ ] Job failure classifier exposes `incomplete_source_coverage`.
- [ ] Full latest-head GitHub CI passes.

## Deliberate deferrals

F05 per-stream incremental watermarks, F06 immutable artifact revisions, partial coverage UX/metadata, GitHub API 1000-result limits, high-signal doc selection, and operator-hosted live import remain independent work. Does not alter or merge Draft PRs #26/#28/#29.
