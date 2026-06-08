## 1. Architecture Inspection

- [x] 1.1 Inspect existing GitHub import, token access source, workspace readiness, auth, and web setup surfaces.
- [x] 1.2 Identify the smallest provider-aware contract that can wrap current GitHub behavior without breaking public import or private token import.

## 2. Backend Contract

- [x] 2.1 Add provider/access-mode normalization helpers for `github`, `gitlab`, `gitee`, and `local`.
- [x] 2.2 Add an admin-only provider-aware setup endpoint that delegates GitHub token setup to the existing private access binding path.
- [x] 2.3 Return bounded unsupported/local-path outcomes for GitLab, Gitee, and local-path setup without echoing token or sensitive path values.
- [x] 2.4 Include safe provider/access-mode metadata in lookup or readiness responses where token-backed workspaces are reported.

## 3. Web Product Surface

- [x] 3.1 Update private repository access setup UI copy and controls to show provider/access mode explicitly.
- [x] 3.2 Preserve existing GitHub token setup behavior and non-admin restrictions.
- [x] 3.3 Display unsupported provider/local-path setup outcomes as operator-guided states rather than generic errors.

## 4. Tests

- [x] 4.1 Add backend API tests for provider-aware setup success, unsupported providers, local-path outcome, non-admin rejection, and token non-echo.
- [x] 4.2 Add or update web tests for provider/access-mode UI behavior and non-admin visibility.
- [x] 4.3 Run targeted backend and web tests.
- [x] 4.4 Run browser/operator rehearsal for the admin setup surface.
  - Verified on restarted local Web/API/Engine stack: GitLab token setup returns `provider_unsupported` and local-path setup returns `local_path_unavailable`; submitted token was cleared and not rendered.

## 5. Documentation and Validation

- [x] 5.1 Update self-hosted/team documentation with the current multi-source support boundary.
- [x] 5.2 Record the update log with implemented scope, limitations, and validation evidence.
- [x] 5.3 Run OpenSpec strict validation for the change.
