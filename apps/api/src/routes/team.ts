import { FastifyInstance, FastifyRequest } from "fastify";
import { z } from "zod";

import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

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

type ForwardInit = Omit<RequestInit, "headers"> & { headers?: Record<string, string> };

async function forwardJson(
  app: FastifyInstance,
  request: FastifyRequest,
  route: string,
  url: string,
  init: ForwardInit = {}
) {
  const env = getEnv();
  const upstream = await fetchUpstreamPayload(
    fetch(`${env.ENGINE_BASE_URL}${url}`, {
      ...init,
      headers: {
        ...(init.body ? { "content-type": "application/json" } : {}),
        ...(await authHeadersForRequest(request)),
        ...(init.headers ?? {}),
      },
    }),
    app.log,
    route
  );
  return upstream;
}

export async function teamRoute(app: FastifyInstance) {
  app.get("/team/accounts", async (request, reply) => {
    const upstream = await forwardJson(app, request, "GET /team/accounts", "/team/accounts");
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts", async (request, reply) => {
    const parsed = accountCreateSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "Invalid account payload", issues: parsed.error.issues });
    }
    const upstream = await forwardJson(app, request, "POST /team/accounts", "/team/accounts", {
      method: "POST",
      body: JSON.stringify(parsed.data),
    });
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/disable", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid account id", issues: params.error.issues });
    }
    const upstream = await forwardJson(
      app,
      request,
      "POST /team/accounts/:actorId/disable",
      `/team/accounts/${params.data.actorId}/disable`,
      { method: "POST" }
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/reset-password", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    const parsed = accountPasswordResetSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid password reset payload" });
    }
    const upstream = await forwardJson(
      app,
      request,
      "POST /team/accounts/:actorId/reset-password",
      `/team/accounts/${params.data.actorId}/reset-password`,
      { method: "POST", body: JSON.stringify(parsed.data) }
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/team/accounts/:actorId/role", async (request, reply) => {
    const params = actorParamsSchema.safeParse(request.params);
    const parsed = accountRoleSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid account role payload" });
    }
    const upstream = await forwardJson(
      app,
      request,
      "POST /team/accounts/:actorId/role",
      `/team/accounts/${params.data.actorId}/role`,
      { method: "POST", body: JSON.stringify(parsed.data) }
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/team/workspaces/:workspaceSlug/members", async (request, reply) => {
    const params = workspaceParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid workspace slug", issues: params.error.issues });
    }
    const upstream = await forwardJson(
      app,
      request,
      "GET /team/workspaces/:workspaceSlug/members",
      `/team/workspaces/${encodeURIComponent(params.data.workspaceSlug)}/members`
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.put("/team/workspaces/:workspaceSlug/members/:actorId", async (request, reply) => {
    const params = workspaceMemberParamsSchema.safeParse(request.params);
    const parsed = accountRoleSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({ error: "Invalid workspace member payload" });
    }
    const upstream = await forwardJson(
      app,
      request,
      "PUT /team/workspaces/:workspaceSlug/members/:actorId",
      `/team/workspaces/${encodeURIComponent(params.data.workspaceSlug)}/members/${params.data.actorId}`,
      { method: "PUT", body: JSON.stringify(parsed.data) }
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.delete("/team/workspaces/:workspaceSlug/members/:actorId", async (request, reply) => {
    const params = workspaceMemberParamsSchema.safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({ error: "Invalid workspace member payload", issues: params.error.issues });
    }
    const upstream = await forwardJson(
      app,
      request,
      "DELETE /team/workspaces/:workspaceSlug/members/:actorId",
      `/team/workspaces/${encodeURIComponent(params.data.workspaceSlug)}/members/${params.data.actorId}`,
      { method: "DELETE" }
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
