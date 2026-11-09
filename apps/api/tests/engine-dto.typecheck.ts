// Compiled by pnpm typecheck, never executed. Unused @ts-expect-error directives fail CI
// if generated contracts or client inference silently widen any of these types.
import type {
  DecisionDetail,
  DecisionListItem,
  DecisionListQuery,
  DecisionReviewRequest,
  DecisionReviewResponse,
  WhyRequest,
  WhyResponse,
} from "@decisionatlas/engine-contract";
import { createDecisionsEngineClient, createWhyEngineClient } from "../src/contracts/engine-client";

export async function whyContractMustRejectDrift() {
  const client = createWhyEngineClient("http://engine.invalid");
  // @ts-expect-error wrong path
  client.POST("/query/whyy", { body: { workspace_slug: "synthetic", question: "why" } });
  // @ts-expect-error wrong method
  client.GET("/query/why");
  // @ts-expect-error missing required question
  client.POST("/query/why", { body: { workspace_slug: "synthetic" } });
  // @ts-expect-error wrong request field type
  const badRequest: WhyRequest = { workspace_slug: 42, question: "why" };
  const { data, error } = await client.POST("/query/why", {
    body: { workspace_slug: "synthetic", question: "why" },
  });
  if (data) {
    const response: WhyResponse = data;
    const answer: string = response.answer;
    // @ts-expect-error response type is generated, not any
    const wrong: number = response.answer;
    // @ts-expect-error unsupported retrieval mode
    response.retrieval_mode = "invented-vector-mode";
    // @ts-expect-error nullable citation URL cannot be assumed to be a string
    const url: string = response.citations[0].url;
    void [answer, wrong, url];
  }
  if (error) {
    // @ts-expect-error error DTO must not be consumed as successful answer
    const answer: string = error.answer;
    void answer;
  }
  void badRequest;
}

export async function decisionsContractMustRejectDrift() {
  const client = createDecisionsEngineClient("http://engine.invalid");
  // @ts-expect-error wrong path
  client.GET("/decisions/{id}");
  // @ts-expect-error wrong method
  client.POST("/decisions");
  // @ts-expect-error required workspace_slug query is missing
  client.GET("/decisions");
  const query: DecisionListQuery = { workspace_slug: "synthetic", review_state: "candidate" };
  const list = await client.GET("/decisions", { params: { query } });
  if (list.data) {
    const item: DecisionListItem = list.data[0];
    const match: boolean | null = item.review_evidence.source_ref_preview[0].current_quote_match;
    const integrity: string = item.review_evidence.current_quote_integrity.status;
    // @ts-expect-error a nullable URL cannot be assumed to be a string
    const url: string = item.review_evidence.primary_artifact.url;
    // @ts-expect-error confidence is a number, not text
    const confidence: string = item.confidence;
    void [match, integrity, url, confidence];
  }

  const detail = await client.GET("/decisions/{decision_id}", {
    params: { path: { decision_id: 1 } },
  });
  if (detail.data) {
    const response: DecisionDetail = detail.data;
    const auditCount: number = response.review_history.length;
    const sourceCount: number = response.source_refs.length;
    void [auditCount, sourceCount];
  }
  // @ts-expect-error required path parameter is missing
  client.GET("/decisions/{decision_id}");

  const body: DecisionReviewRequest = { review_state: "accepted", review_rationale: null };
  const reviewed = await client.POST("/decisions/{decision_id}/review", {
    params: { path: { decision_id: 1 } },
    body,
  });
  if (reviewed.data) {
    const response: DecisionReviewResponse = reviewed.data;
    const action: string = response.audit_event.action;
    // @ts-expect-error audit history is an array, not a string
    const history: string = response.review_history;
    void [action, history];
  }
  // @ts-expect-error review_state is a string, not a number
  const invalidBody: DecisionReviewRequest = { review_state: 42 };
  // @ts-expect-error required review_state is missing
  client.POST("/decisions/{decision_id}/review", { params: { path: { decision_id: 1 } }, body: {} });
  void invalidBody;
}
import type {
  GitHubImportRequest,
  GitHubPrivateAccessBindingRequest,
  ImportCapabilitiesResponse,
  ImportJobResponse,
  ImportTargetResponse,
} from "@decisionatlas/engine-contract";
import { createImportsEngineClient } from "../src/contracts/engine-client";

export async function importsContractMustRejectDrift() {
  const client = createImportsEngineClient("http://engine.invalid");
  // @ts-expect-error unknown route must not be admitted
  client.GET("/imports/{job_id}/cancel");
  // @ts-expect-error wrong method
  client.DELETE("/imports/github");
  // @ts-expect-error required lookup query is missing
  client.GET("/imports/lookup");
  const lookup = await client.GET("/imports/lookup", { params: { query: { repo: "org/repo" } } });
  if (lookup.data) {
    const target: ImportTargetResponse = lookup.data;
    const hasActive: boolean = target.has_running_import;
    const latest: ImportJobResponse | null = target.latest_import;
    // @ts-expect-error access token must never appear in a response DTO
    const leakedToken: string = target.token;
    void [hasActive, latest, leakedToken];
  }

  const job = await client.GET("/imports/{job_id}", { params: { path: { job_id: "job-123" } } });
  if (job.data) {
    const response: ImportJobResponse = job.data;
    const status: "queued" | "running" | "paused" | "succeeded" | "failed" = response.status;
    const count: number = response.imported_count;
    // @ts-expect-error status is a finite state, not an arbitrary string
    const invalidStatus: "cancelled" = response.status;
    void [status, count, invalidStatus];
  }
  // @ts-expect-error required path parameter is missing
  client.GET("/imports/{job_id}");

  const body: GitHubImportRequest = { repo: "org/repo", mode: "since_last_sync" };
  client.POST("/imports/github", { body });
  // @ts-expect-error repo is required
  client.POST("/imports/github", { body: { mode: "full" } });

  const privateBody: GitHubPrivateAccessBindingRequest = { repo: "org/private", token: "ghp-secret" };
  client.POST("/imports/github/private-access/bind", { body: privateBody });
  // @ts-expect-error private-access token is required in the request
  client.POST("/imports/github/private-access/bind", { body: { repo: "org/private" } });
  // @ts-expect-error credentials are never part of a response
  const invalidTarget: ImportTargetResponse = { token: "ghp-secret" };

  const capabilities = await client.GET("/imports/capabilities");
  if (capabilities.data) {
    const response: ImportCapabilitiesResponse = capabilities.data;
    const enabled: boolean = response.pause_resume.enabled;
    void enabled;
  }
  void invalidTarget;
}

import type {
  AuthBootstrapResponse,
  AuthLoginResponse,
  AuthSessionResponse,
  LoginRequest,
  ScopeSwitchRequest,
  TeamAccountCreateRequest,
  TeamAccountListResponse,
  TeamAccountPasswordResetRequest,
  TeamAccountResponse,
  TeamAccountRoleRequest,
  TeamRole,
  WorkspaceMemberListResponse,
  WorkspaceMemberResponse,
  WorkspaceMemberRoleRequest,
} from "@decisionatlas/engine-contract";
import { createAuthEngineClient, createTeamEngineClient } from "../src/contracts/engine-client";

export async function authTeamContractsMustRejectDrift() {
  const auth = createAuthEngineClient("http://engine.invalid");
  // @ts-expect-error wrong Auth path
  auth.POST("/auth/log-in");
  // @ts-expect-error wrong HTTP method for login
  auth.GET("/auth/login");
  // @ts-expect-error login password is required
  auth.POST("/auth/login", { body: { username: "operator" } });
  const loginBody: LoginRequest = { username: "operator", password: "secret" };
  const login = await auth.POST("/auth/login", { body: loginBody });
  if (login.data) {
    const response: AuthLoginResponse = login.data;
    const status: "active" | "disabled" = response.actor.status;
    const scopeCount: number = response.available_scopes.length;
    // @ts-expect-error role is a finite enum
    const invalidRole: "owner" = response.role;
    void [status, scopeCount, invalidRole];
  }

  const bootstrap = await auth.POST("/auth/bootstrap");
  if (bootstrap.data) {
    const response: AuthBootstrapResponse = bootstrap.data;
    // @ts-expect-error bootstrap response intentionally has no available_scopes
    const scopes = response.available_scopes;
    void scopes;
  }

  const session = await auth.GET("/auth/session");
  if (session.data) {
    const response: AuthSessionResponse = session.data;
    const token: string = response.session_token;
    // @ts-expect-error session actor response intentionally omits login/bootstrap status
    const status = response.actor.status;
    void [token, status];
  }
  const scopeBody: ScopeSwitchRequest = { owner_scope: "team-a" };
  auth.POST("/auth/scope", { body: scopeBody });

  const team = createTeamEngineClient("http://engine.invalid");
  // @ts-expect-error unknown Team path
  team.GET("/team/account");
  // @ts-expect-error wrong HTTP method for account role update
  team.GET("/team/accounts/{actor_id}/role");
  // @ts-expect-error required actor_id path parameter is missing
  team.POST("/team/accounts/{actor_id}/disable");
  // @ts-expect-error account create password is required
  team.POST("/team/accounts", { body: { username: "new-user" } });
  const createBody: TeamAccountCreateRequest = { username: "new-user", password: "password123", role: "reviewer" };
  team.POST("/team/accounts", { body: createBody });
  const resetBody: TeamAccountPasswordResetRequest = { password: "password123" };
  team.POST("/team/accounts/{actor_id}/reset-password", {
    params: { path: { actor_id: 2 } },
    body: resetBody,
  });
  const roleBody: TeamAccountRoleRequest = { role: "reviewer" };
  team.POST("/team/accounts/{actor_id}/role", {
    params: { path: { actor_id: 2 } },
    body: roleBody,
  });
  const members = await team.GET("/team/workspaces/{workspace_slug}/members", {
    params: { path: { workspace_slug: "demo-workspace" } },
  });
  if (members.data) {
    const response: WorkspaceMemberListResponse = members.data;
    const member: WorkspaceMemberResponse | undefined = response.members[0];
    const role: TeamRole | null = member?.actor.role ?? null;
    // @ts-expect-error workspace actor role is nullable and finite
    const invalidRole: "owner" = member?.actor.role;
    void [role, invalidRole];
  }
  // @ts-expect-error workspace assignment requires role
  team.PUT("/team/workspaces/{workspace_slug}/members/{actor_id}", {
    params: { path: { workspace_slug: "demo-workspace", actor_id: 2 } },
    body: {},
  });
  // @ts-expect-error Team account DTO must not expose credentials
  const leakedPassword: string = ({} as TeamAccountResponse).password;
  // @ts-expect-error Team account DTO must not expose session credentials
  const leakedToken: string = ({} as TeamAccountResponse).session_token;
  const validRole: TeamRole = "viewer";
  const validMember: WorkspaceMemberResponse = {
    workspace_id: 1,
    actor: { id: 2, username: "viewer", display_name: null, status: "active", bootstrap: false, role: null },
    role: "viewer",
  };
  const validAccount: TeamAccountResponse = {
    id: 2, username: "viewer", display_name: null, status: "active", bootstrap: false, role: "viewer",
  };
  const validAccounts: TeamAccountListResponse = { accounts: [validAccount] };
  const workspaceMemberRole: WorkspaceMemberRoleRequest = { role: "viewer" };
  void [leakedPassword, leakedToken, validRole, validMember, validAccounts, workspaceMemberRole];
}
