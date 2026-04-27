## Why

DecisionAtlas already has backend support for actors, sessions, owner scopes, and scoped workspace actions, but those platform concepts are not yet productized in the web experience. Before GitHub App onboarding or private repository access can become usable, users need a clear login/session surface and a visible current owner scope.

## What Changes

- Add a product login/session flow that turns the existing backend auth API into a visible web experience.
- Add current owner-scope display and scope switching in the product shell.
- Make workspace navigation and imported workspace actions resolve through the current owner scope so users understand which workspace boundary they are operating in.
- Preserve the current local bootstrap path for demo and developer usage.
- Keep GitHub App installation onboarding and private repository credential setup out of scope for this change.

## Capabilities

### New Capabilities
- `scope-switching-product-flow`: Defines the user-facing login, current-scope display, scope switching, and scoped workspace navigation behavior.

### Modified Capabilities
- `login-roles-and-workspace-scoping`: Productizes the existing auth/session/scope requirements into visible login and session recovery behavior.
- `platform-foundation`: Clarifies that workspace ownership and product actions must be visible in the product shell before GitHub App and private repo flows are added.

## Impact

- Affected web areas: app shell/navigation, homepage entry state, login UI, workspace dashboard/search/review/timeline/drift entry points, tests.
- Affected API areas: existing Fastify auth proxy routes may need small response/cookie handling refinements.
- Affected engine areas: existing auth/session/scope endpoints may need minor payload additions for display labels, but no new auth model is expected.
- Affected docs/specs: platform productization order and auth/scope behavior.
