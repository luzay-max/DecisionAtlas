## Why

DecisionAtlas now supports self-hosted team accounts and has proven public GitHub import with real benchmark evidence, but the product plan requires administrators to connect multiple Git sources through token or local-path setup. This change starts that P1 track by introducing a unified Git source model and admin-safe token/import workflow that can grow beyond GitHub without weakening credential boundaries.

## What Changes

- Add a `git-source-token-import` capability for provider-aware repository access configuration.
- Extend admin-facing repository access setup from GitHub-only language toward provider, access mode, repository identifier, credential reference, authorization status, and workspace slug.
- Keep GitHub token import executable through the existing private-access binding path while adding explicit provider/access-mode metadata for future GitLab, Gitee, and local-path support.
- Represent unsupported or not-yet-implemented providers as bounded setup outcomes instead of generic failures.
- Preserve security rules: token values are accepted only from admins, are never returned to clients, and are not written into evidence/history output.
- No breaking changes.

## Capabilities

### New Capabilities

- `git-source-token-import`: Covers provider-aware Git source setup, token/local-path access modes, safe credential handling, and bounded import/setup outcomes.

### Modified Capabilities

- `live-repository-analysis`: Add provider/access-mode-aware live-analysis setup and outcome reporting before import/reuse actions.
- `imported-workspace-readiness-surface`: Add provider/access-mode metadata to imported readiness without exposing credential material.
- `private-repo-access-product-flow`: Generalize the admin setup surface from GitHub private token only to provider-aware token setup while retaining existing GitHub behavior.

## Impact

- Affected code: Engine import/access APIs, repository access metadata, API/web client types, admin/team import UI, tests, and self-hosted documentation.
- Affected systems: self-hosted admin setup flow, workspace readiness evidence, live import outcome classification, and future multi-provider integration.
- Out of scope for this change: full GitLab/Gitee API ingestion parity, SaaS OAuth, GitHub App marketplace flow, enterprise SSO, and billing.
