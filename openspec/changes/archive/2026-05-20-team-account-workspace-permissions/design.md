## Context

DecisionAtlas already has a local bootstrap admin identity, login/session APIs, owner-scope membership, and frontend role gates. That is enough for local evaluation, but not enough for the planned Team Self-hosted product where a small team deploys one server, an administrator creates accounts, reviewers handle decision governance, and viewers consume decision memory without mutation rights.

The current model is owner-scope centric. This change should keep that foundation while adding explicit administrator-managed accounts and workspace-level membership so a team can safely share one self-hosted instance across multiple repositories.

## Goals / Non-Goals

**Goals:**

- Let an admin create, disable, and reset passwords for local self-hosted users.
- Let an admin assign admin/reviewer/viewer roles to users.
- Let an admin bind users to specific workspaces or owner-scope defaults.
- Enforce permissions in backend routes, not only in frontend components.
- Keep bootstrap local admin available for development, first-run setup, and recovery.
- Make viewer role truly read-only across review, import, governance mutation, private access, and account-management flows.

**Non-Goals:**

- Do not add public signup, email invitation, forgot-password email, SSO, OIDC, SAML, SaaS tenant billing, or Marketplace OAuth.
- Do not implement GitHub/GitLab/Gitee/local repository provider expansion in this change; that is the next planned change.
- Do not build a Git hosting, code review, issue, or CI/CD replacement.
- Do not add strong runtime license enforcement.

## Decisions

1. Build on owner-scope roles, add workspace membership where needed.

   Owner-scope membership remains the broad team boundary. Workspace membership adds tighter visibility for teams with multiple repositories. If a workspace has no explicit member rows, owner-scope membership can continue to grant access for backward compatibility; once workspace members exist, visibility and actions should be evaluated against workspace membership plus role.

2. Administrator-created local accounts are the first self-hosted account model.

   Manual account creation matches the product direction: small teams, offline/self-hosted deployment, no SaaS signup. Password reset is admin-triggered and local. This avoids email infrastructure and external identity dependencies.

3. Disabled accounts keep historical attribution.

   Disabling an actor should prevent login and future actions, but historical review/action records should remain associated with the actor. Deleting users would damage auditability and is not needed for the first team version.

4. Permission enforcement happens in engine/API routes and UI gates.

   UI gating improves product clarity, but engine/API authorization is the source of truth. Import, private access, member management, review, drift mutation, and governance mutation must reject insufficient roles even if a user bypasses the UI.

5. Bootstrap admin remains visible and recoverable.

   Bootstrap mode is still required for local development and first-run recovery. It should be clearly marked as local bootstrap and should be able to create the first real admin account.

## Risks / Trade-offs

- Workspace membership can conflict with existing owner-scope assumptions -> preserve owner-scope fallback until explicit workspace membership is configured.
- Manual password management can become weak operationally -> require admin reset flow and document that production teams should rotate initial passwords.
- Frontend-only role gates can be bypassed -> add backend permission tests for every sensitive route touched by this change.
- Disabled users may still hold valid session cookies -> session recovery and route authorization must reject disabled actors.
- This change can grow too large -> keep Git provider expansion, token encryption improvements, audit trail deepening, and reporting for later OpenSpec changes.
