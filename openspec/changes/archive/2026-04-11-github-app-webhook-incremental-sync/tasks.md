## 1. Installation and Access-Source Foundations

- [x] 1.1 Add owner-scoped GitHub App installation / access-source persistence and repository binding models.
- [x] 1.2 Update repository lookup and imported-workspace resolution to recognize installation-backed workspaces within the current owner scope.
- [x] 1.3 Backfill or normalize existing imported workspaces so manual/public access remains a valid baseline when no installation binding exists.

## 2. Webhook-Driven Incremental Sync

- [x] 2.1 Add bounded GitHub webhook ingestion that resolves installation, repository, and owner-scoped workspace identity.
- [x] 2.2 Reuse the existing `since_last_sync` import path for qualifying webhook-triggered sync jobs.
- [x] 2.3 Prevent duplicate webhook-triggered sync enqueue when a workspace already has an active queued or running sync.

## 3. Product State and Validation

- [x] 3.1 Expose latest sync origin, latest sync timestamp, and bounded recent sync history in reusable workspace-facing APIs.
- [x] 3.2 Update dashboard/search or other imported-workspace surfaces to describe installation-backed reuse and latest sync state clearly.
- [x] 3.3 Add regression coverage for installation-backed lookup, webhook-triggered incremental sync, and sync provenance while preserving current benchmark and pre-release baselines.
