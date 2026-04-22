import { FastifyInstance } from "fastify";
import { z } from "zod";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { logInfo } from "../plugins/logging";
import { fetchUpstreamPayload } from "../proxy";

const githubImportSchema = z.object({
  workspace_slug: z.string().min(1).optional(),
  repo: z.string().min(3),
  mode: z.enum(["full", "since_last_sync"]).default("full"),
  owner_scope: z.string().min(1).optional(),
  access_source_type: z.string().min(1).optional(),
  access_source_ref: z.string().min(1).optional(),
});

const installationBindingSchema = z.object({
  repo: z.string().min(3),
  installation_id: z.string().min(1),
  owner_scope: z.string().min(1).optional(),
  account_login: z.string().min(1).optional(),
  account_type: z.string().min(1).optional(),
  workspace_slug: z.string().min(1).optional(),
});

const privateAccessBindingSchema = z.object({
  repo: z.string().min(3),
  token: z.string().min(1),
  owner_scope: z.string().min(1).optional(),
  source_ref: z.string().min(1).optional(),
  source_label: z.string().min(1).optional(),
  workspace_slug: z.string().min(1).optional(),
});

const webhookHeadersSchema = z.object({
  "x-github-event": z.string().min(1),
  "x-github-delivery": z.string().min(1).optional(),
  "x-hub-signature-256": z.string().min(1).optional(),
});

export async function importsRoute(app: FastifyInstance) {
  app.get("/imports/lookup", async (request, reply) => {
    const query = z.object({ repo: z.string().min(3) }).safeParse(request.query);
    if (!query.success) {
      return reply.status(400).send({
        error: "Invalid lookup query",
        issues: query.error.issues
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/lookup?repo=${encodeURIComponent(query.data.repo)}`, {
        headers: authHeaders,
      }),
      app.log,
      "GET /imports/lookup"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/imports/github", async (request, reply) => {
    const parsed = githubImportSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid request payload",
        issues: parsed.error.issues
      });
    }

    const payload = parsed.data;
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    logInfo(app.log, "github import requested", { job_id: "pending" });

    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/github`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(payload)
      }),
      app.log,
      "POST /imports/github"
    );
    const json = upstream.payload as Record<string, unknown> | null;
    logInfo(app.log, "github import completed", {
      job_id: typeof json?.job_id === "string" ? json.job_id : "unknown"
    });
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/imports/github/installations/bind", async (request, reply) => {
    const parsed = installationBindingSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid installation binding payload",
        issues: parsed.error.issues
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/github/installations/bind`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(parsed.data)
      }),
      app.log,
      "POST /imports/github/installations/bind"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/imports/github/private-access/bind", async (request, reply) => {
    const parsed = privateAccessBindingSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid private access binding payload",
        issues: parsed.error.issues
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/github/private-access/bind`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(parsed.data)
      }),
      app.log,
      "POST /imports/github/private-access/bind"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/imports/github/webhook", async (request, reply) => {
    const headers = webhookHeadersSchema.safeParse(request.headers);
    if (!headers.success) {
      return reply.status(400).send({
        error: "Invalid webhook headers",
        issues: headers.error.issues
      });
    }

    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/github/webhook`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-github-event": headers.data["x-github-event"],
          ...(headers.data["x-github-delivery"]
            ? { "x-github-delivery": headers.data["x-github-delivery"] }
            : {}),
          ...(headers.data["x-hub-signature-256"]
            ? { "x-hub-signature-256": headers.data["x-hub-signature-256"] }
            : {}),
        },
        body: JSON.stringify(request.body ?? {})
      }),
      app.log,
      "POST /imports/github/webhook"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/imports/:jobId", async (request, reply) => {
    const params = z.object({ jobId: z.string().min(1) }).safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({
        error: "Invalid import job id",
        issues: params.error.issues
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/${params.data.jobId}`, { headers: authHeaders }),
      app.log,
      "GET /imports/:jobId"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
