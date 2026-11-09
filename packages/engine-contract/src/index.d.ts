import type { paths, components } from "./openapi.generated";
export type { paths, components, operations } from "./openapi.generated";

export type WhyRequest = paths["/query/why"]["post"]["requestBody"]["content"]["application/json"];
export type WhyResponse = paths["/query/why"]["post"]["responses"][200]["content"]["application/json"];
export type WhyStatus = components["schemas"]["WhyAnswerResponse"]["status"];
export type RetrievalMode = NonNullable<WhyResponse["retrieval_mode"]>;
export type WorkspaceReadiness = components["schemas"]["WorkspaceReadiness"];

export type DecisionListQuery = paths["/decisions"]["get"]["parameters"]["query"];
export type DecisionListItem = paths["/decisions"]["get"]["responses"][200]["content"]["application/json"][number];
export type DecisionDetail = paths["/decisions/{decision_id}"]["get"]["responses"][200]["content"]["application/json"];
export type DecisionReviewRequest = paths["/decisions/{decision_id}/review"]["post"]["requestBody"]["content"]["application/json"];
export type DecisionReviewResponse = paths["/decisions/{decision_id}/review"]["post"]["responses"][200]["content"]["application/json"];
export type DecisionSourceRef = components["schemas"]["DecisionSourceRefResponse"];
export type DecisionAuditEvent = components["schemas"]["DecisionAuditEventResponse"];
export type DecisionWorkspaceMode = DecisionListItem["workspace_mode"];

export type ImportLookupQuery = paths["/imports/lookup"]["get"]["parameters"]["query"];
export type GitHubImportRequest = paths["/imports/github"]["post"]["requestBody"]["content"]["application/json"];
export type GitHubInstallationBindingRequest = paths["/imports/github/installations/bind"]["post"]["requestBody"]["content"]["application/json"];
export type GitHubPrivateAccessBindingRequest = paths["/imports/github/private-access/bind"]["post"]["requestBody"]["content"]["application/json"];
export type GitSourceBindingRequest = paths["/imports/git-sources/bind"]["post"]["requestBody"]["content"]["application/json"];
export type ImportJobResponse = paths["/imports/{job_id}"]["get"]["responses"][200]["content"]["application/json"];
export type ImportTargetResponse = paths["/imports/lookup"]["get"]["responses"][200]["content"]["application/json"];
export type ImportCapabilitiesResponse = paths["/imports/capabilities"]["get"]["responses"][200]["content"]["application/json"];
export type GitHubWebhookResponse = paths["/imports/github/webhook"]["post"]["responses"][200]["content"]["application/json"];

export type LoginRequest = paths["/auth/login"]["post"]["requestBody"]["content"]["application/json"];
export type ScopeSwitchRequest = paths["/auth/scope"]["post"]["requestBody"]["content"]["application/json"];
export type AuthBootstrapResponse = paths["/auth/bootstrap"]["post"]["responses"][200]["content"]["application/json"];
export type AuthLoginResponse = paths["/auth/login"]["post"]["responses"][200]["content"]["application/json"];
export type AuthLogoutResponse = paths["/auth/logout"]["post"]["responses"][200]["content"]["application/json"];
export type AuthSessionResponse = paths["/auth/session"]["get"]["responses"][200]["content"]["application/json"];
export type AuthScopeSwitchResponse = paths["/auth/scope"]["post"]["responses"][200]["content"]["application/json"];
export type AuthOwnerScopeMembershipResponse = components["schemas"]["AuthOwnerScopeMembershipResponse"];

export type TeamAccountCreateRequest = paths["/team/accounts"]["post"]["requestBody"]["content"]["application/json"];
export type TeamAccountRoleRequest = paths["/team/accounts/{actor_id}/role"]["post"]["requestBody"]["content"]["application/json"];
export type TeamAccountPasswordResetRequest = paths["/team/accounts/{actor_id}/reset-password"]["post"]["requestBody"]["content"]["application/json"];
export type WorkspaceMemberRoleRequest = paths["/team/workspaces/{workspace_slug}/members/{actor_id}"]["put"]["requestBody"]["content"]["application/json"];
export type TeamRole = components["schemas"]["TeamAccountResponse"]["role"];
export type TeamAccountResponse = components["schemas"]["TeamAccountResponse"];
export type TeamAccountListResponse = paths["/team/accounts"]["get"]["responses"][200]["content"]["application/json"];
export type TeamAccountMutationResponse = paths["/team/accounts"]["post"]["responses"][200]["content"]["application/json"];
export type WorkspaceMemberResponse = components["schemas"]["TeamWorkspaceMemberResponse"];
export type WorkspaceMemberListResponse = paths["/team/workspaces/{workspace_slug}/members"]["get"]["responses"][200]["content"]["application/json"];
export type WorkspaceMemberMutationResponse = paths["/team/workspaces/{workspace_slug}/members/{actor_id}"]["put"]["responses"][200]["content"]["application/json"];
export type WorkspaceMemberRemovalResponse = paths["/team/workspaces/{workspace_slug}/members/{actor_id}"]["delete"]["responses"][200]["content"]["application/json"];
