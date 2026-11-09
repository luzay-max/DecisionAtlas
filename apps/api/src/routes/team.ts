import { FastifyInstance } from "fastify";
import { z } from "zod";

import type {
  TeamAccountCreateRequest,
  TeamAccountPasswordResetRequest,
  TeamAccountRoleRequest,
  WorkspaceMemberRoleRequest,
} from "@decisionatlas/engine-contract";
import { authHeadersForRequest } from "../auth";
import { createTeamEngineClient, forwardContractTextRequest } from "../contracts/engine-client";
import { getEnv } from "../plugins/env";

const roleSchema = z.enum(["viewer", "reviewer", "admin"]);

const accountCreateSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(8),
  display_name: z.string().min(1).optional(),
  role: roleSchema.default("viewer"),
});

const accountRoleSchema = z.object({
  role: roleSchema,
});

const accountPasswordResetSchema = z.object({
  password: z.string().min(8),
});

const actorParamsSchema = z.object({
  actorId: z.coerce.number().int().positive(),
});

const workspaceParamsSchema = z.object({
  workspaceSlug: z.string().min(1),
});

const workspaceMemberParamsSchema = z.object({
  workspaceSlug: z.string().min(1),
  actorId: z.coerce.number().int().positive(),
});

export async function teamRoute(app: FastifyInstance) {
  app.get("/team/accounts", async (request, reply) => {
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.GET("/team/accounts", { headers: await authHeadersForRequest(request), parseAs: "text" }),
      app.log,
      "GET /team/accounts",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts", async (request, reply) => {
    const parsed = accountCreateSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "Invalid account payload", issues: parsed.error.issues });
    }
    const body: TeamAccountCreateRequest = parsed.data;
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.POST("/team/accounts", {
        body,
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "POST /team/accounts",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/disable", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid account id", issues: params.error.issues });
    }
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.POST("/team/accounts/{actor_id}/disable", {
        params: { path: { actor_id: params.data.actorId } },
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "POST /team/accounts/:actorId/disable",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/reset-password", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    const parsed = accountPasswordResetSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid password reset payload" });
    }
    const body: TeamAccountPasswordResetRequest = parsed.data;
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.POST("/team/accounts/{actor_id}/reset-password", {
        params: { path: { actor_id: params.data.actorId } },
        body,
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "POST /team/accounts/:actorId/reset-password",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/role", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    const parsed = accountRoleSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid account role payload" });
    }
    const body: TeamAccountRoleRequest = parsed.data;
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.POST("/team/accounts/{actor_id}/role", {
        params: { path: { actor_id: params.data.actorId } },
        body,
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "POST /team/accounts/:actorId/role",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/team/workspaces/:workspaceSlug/members", async (request, reply) => {
    const params = workspaceParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid workspace slug", issues: params.error.issues });
    }
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.GET("/team/workspaces/{workspace_slug}/members", {
        params: { path: { workspace_slug: params.data.workspaceSlug } },
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "GET /team/workspaces/:workspaceSlug/members",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.put("/team/workspaces/:workspaceSlug/members/:actorId", async (request, reply) => {
    const params = workspaceMemberParamsSchema.safeParse(request.params);
    const parsed = accountRoleSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid workspace member payload" });
    }
    const body: WorkspaceMemberRoleRequest = parsed.data;
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.PUT("/team/workspaces/{workspace_slug}/members/{actor_id}", {
        params: { path: { workspace_slug: params.data.workspaceSlug, actor_id: params.data.actorId } },
        body,
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "PUT /team/workspaces/:workspaceSlug/members/:actorId",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.delete("/team/workspaces/:workspaceSlug/members/:actorId", async (request, reply) => {
    const params = workspaceMemberParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid workspace member payload", issues: params.error.issues });
    }
    const client = createTeamEngineClient(getEnv().ENGINE_BASE_URL);
    const upstream = await forwardContractTextRequest(
      client.DELETE("/team/workspaces/{workspace_slug}/members/{actor_id}", {
        params: { path: { workspace_slug: params.data.workspaceSlug, actor_id: params.data.actorId } },
        headers: await authHeadersForRequest(request),
        parseAs: "text",
      }),
      app.log,
      "DELETE /team/workspaces/:workspaceSlug/members/:actorId",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
