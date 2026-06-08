## Context

DecisionAtlas already has public GitHub import, GitHub token-backed private access, owner-scoped team permissions, and readiness/benchmark evidence. The next product milestone is not a full Git hosting platform; it is an admin-controlled self-hosted import surface that can represent GitHub, GitLab, Gitee, and local repositories safely and consistently.

The current implementation has GitHub-specific concepts in API routes, repository access records, and UI copy. This change introduces a provider-aware boundary without forcing full ingestion parity for every provider in one step.

## Goals / Non-Goals

**Goals:**

- Introduce a unified Git source contract with provider, access mode, repository identifier, credential reference, authorization status, workspace slug, and bounded setup outcome.
- Keep GitHub public/token import working through the existing path.
- Add explicit placeholder outcomes for GitLab, Gitee, and local-path setup so the UI and evidence do not collapse unsupported providers into generic errors.
- Preserve admin-only token submission and never return raw token material.
- Expose provider/access-mode metadata in readiness and live-analysis outcomes.

**Non-Goals:**

- Do not implement complete GitLab/Gitee API ingestion parity in this change.
- Do not add OAuth, GitHub App marketplace installation, SaaS billing, SSO, or multi-tenant hosted operations.
- Do not implement a secret vault; token storage remains within the current self-hosted server boundary.
- Do not make live private repository import part of default CI.

## Decisions

1. Add provider-aware metadata before adding every provider's full importer.
   - Rationale: the product needs honest setup/status reporting before it needs every ingestion backend.
   - Alternative considered: add GitLab/Gitee importers immediately. Rejected because it expands network/provider complexity before the credential and permission boundary is proven.

2. Keep GitHub token import as the first executable provider.
   - Rationale: existing APIs and tests already validate token-backed private GitHub access and no-token public GitHub import.
   - Alternative considered: rewrite import APIs around a generic `/imports/git-source` endpoint first. Rejected because it risks destabilizing proven GitHub flows.

3. Represent unsupported providers as bounded setup outcomes.
   - Rationale: admins should see "provider not implemented yet" or "local path requires server operator setup" rather than ambiguous provider/network failures.
   - Alternative considered: hide unsupported providers. Rejected because the roadmap needs visible product scaffolding and documentation.

4. Treat local path as a server-side import mode.
   - Rationale: self-hosted/offline deployments can mount repositories on the server; browser upload or desktop sync is out of scope.
   - Alternative considered: upload zip archives. Deferred because it changes storage, security scanning, and operator UX.

## Risks / Trade-offs

- [Credential leakage] -> Keep tokens write-only, never return token values, add tests that assert submitted tokens are absent from responses.
- [Provider scope creep] -> Limit this change to provider metadata and GitHub executable behavior; defer full GitLab/Gitee ingestion.
- [Confusing UI placeholders] -> Label non-GitHub providers as setup or not-yet-implemented states, not failed imports.
- [Local-path security] -> Treat local path as server-operator-guided and do not allow arbitrary browser users to read server paths without admin role.
