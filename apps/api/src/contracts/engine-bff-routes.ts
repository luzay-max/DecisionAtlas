import type { EngineRoute } from "./engine-routes.generated";

type BffMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

type BffEngineRoute = {
  engine: EngineRoute;
  bffMethod: BffMethod;
  bffPath: string;
};

// Explicit mapping from Engine operations to registered Fastify BFF routes.
// The Engine side is checked against generated FastAPI OpenAPI types; tests
// verify that each BFF method/path is actually registered by buildServer().
export const ENGINE_BFF_ROUTES = [
  { engine: "POST /auth/bootstrap", bffMethod: "POST", bffPath: "/auth/bootstrap" },
  { engine: "POST /auth/logout", bffMethod: "POST", bffPath: "/auth/logout" },
  { engine: "POST /auth/login", bffMethod: "POST", bffPath: "/auth/login" },
  { engine: "GET /auth/session", bffMethod: "GET", bffPath: "/auth/session" },
  { engine: "POST /auth/scope", bffMethod: "POST", bffPath: "/auth/scope" },
  { engine: "GET /dashboard/summary", bffMethod: "GET", bffPath: "/dashboard/summary" },
  { engine: "GET /decisions", bffMethod: "GET", bffPath: "/decisions" },
  { engine: "GET /decisions/{decision_id}", bffMethod: "GET", bffPath: "/decisions/:id" },
  { engine: "POST /decisions/{decision_id}/review", bffMethod: "POST", bffPath: "/decisions/:id/review" },
  { engine: "GET /drift", bffMethod: "GET", bffPath: "/drift" },
  { engine: "POST /drift/evaluate", bffMethod: "POST", bffPath: "/drift/evaluate" },
  { engine: "POST /drift/alerts/{alert_id}/disposition", bffMethod: "POST", bffPath: "/drift/alerts/:alertId/disposition" },
  { engine: "POST /governance/documents", bffMethod: "POST", bffPath: "/governance/documents" },
  { engine: "GET /governance/documents", bffMethod: "GET", bffPath: "/governance/documents" },
  { engine: "GET /governance/rules", bffMethod: "GET", bffPath: "/governance/rules" },
  { engine: "POST /governance/rules/{draft_id}/review", bffMethod: "POST", bffPath: "/governance/rules/:draftId/review" },
  { engine: "GET /governance/guardrail", bffMethod: "GET", bffPath: "/governance/guardrail" },
  { engine: "GET /imports/lookup", bffMethod: "GET", bffPath: "/imports/lookup" },
  { engine: "POST /imports/github", bffMethod: "POST", bffPath: "/imports/github" },
  { engine: "POST /imports/github/installations/bind", bffMethod: "POST", bffPath: "/imports/github/installations/bind" },
  { engine: "POST /imports/github/private-access/bind", bffMethod: "POST", bffPath: "/imports/github/private-access/bind" },
  { engine: "POST /imports/git-sources/bind", bffMethod: "POST", bffPath: "/imports/git-sources/bind" },
  { engine: "POST /imports/github/webhook", bffMethod: "POST", bffPath: "/imports/github/webhook" },
  { engine: "POST /imports/{job_id}/pause", bffMethod: "POST", bffPath: "/imports/:jobId/pause" },
  { engine: "POST /imports/{job_id}/resume", bffMethod: "POST", bffPath: "/imports/:jobId/resume" },
  { engine: "GET /imports/capabilities", bffMethod: "GET", bffPath: "/imports/capabilities" },
  { engine: "GET /imports/{job_id}", bffMethod: "GET", bffPath: "/imports/:jobId" },
  { engine: "POST /query/why", bffMethod: "POST", bffPath: "/query/why" },
  { engine: "GET /runtime/provider-mode", bffMethod: "GET", bffPath: "/runtime/provider-mode" },
  { engine: "POST /runtime/provider-mode", bffMethod: "POST", bffPath: "/runtime/provider-mode" },
  { engine: "GET /team/accounts", bffMethod: "GET", bffPath: "/team/accounts" },
  { engine: "POST /team/accounts", bffMethod: "POST", bffPath: "/team/accounts" },
  { engine: "POST /team/accounts/{actor_id}/disable", bffMethod: "POST", bffPath: "/team/accounts/:actorId/disable" },
  { engine: "POST /team/accounts/{actor_id}/reset-password", bffMethod: "POST", bffPath: "/team/accounts/:actorId/reset-password" },
  { engine: "POST /team/accounts/{actor_id}/role", bffMethod: "POST", bffPath: "/team/accounts/:actorId/role" },
  { engine: "GET /team/workspaces/{workspace_slug}/members", bffMethod: "GET", bffPath: "/team/workspaces/:workspaceSlug/members" },
  { engine: "PUT /team/workspaces/{workspace_slug}/members/{actor_id}", bffMethod: "PUT", bffPath: "/team/workspaces/:workspaceSlug/members/:actorId" },
  { engine: "DELETE /team/workspaces/{workspace_slug}/members/{actor_id}", bffMethod: "DELETE", bffPath: "/team/workspaces/:workspaceSlug/members/:actorId" },
  { engine: "GET /timeline", bffMethod: "GET", bffPath: "/timeline" },
] as const satisfies readonly BffEngineRoute[];
