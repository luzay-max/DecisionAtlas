## Why

DecisionAtlas now has owner-scoped workspace, GitHub App, and private-repository access foundations, but product actions are still effectively anonymous. The next bottleneck is not repository access itself; it is identifying who is acting, which owner scope they are acting in, and what they are allowed to do.

## What Changes

- Add explicit login-backed actor identity for product actions in the imported-workspace lane.
- Add owner-scope membership and product roles so view, import, sync, review, accept, and drift actions can be enforced consistently.
- Scope dashboard, search, live-analysis lookup, and workspace pages to the current owner scope instead of relying on global visibility.
- Preserve the current single-user local baseline through a default bootstrap owner/admin path.
- Defer advanced organization management, SSO, and billing concerns.

## Capabilities

### New Capabilities
- `login-roles-and-workspace-scoping`: Login-backed actor identity, owner-scope membership, and product-role enforcement for workspace actions.

### Modified Capabilities
- `platform-foundation`: Product-action permissions become concrete role assignments tied to actor identity and owner scopes.
- `live-repository-analysis`: Repository lookup and import entry must resolve through the current authenticated owner scope.
- `workspace-reuse-and-incremental-sync`: Reuse, sync, and workspace visibility must be enforced through authenticated scope membership rather than anonymous access.

## Impact

- Engine auth/session model, actor resolution, and authorization checks
- Owner-scope membership and role persistence
- API request context for dashboard, search, import, review, and drift flows
- Frontend session handling and owner-scope selection/persistence
- Migration/backfill for current single-user local workspaces
