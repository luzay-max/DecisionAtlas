import { FastifyInstance, FastifyRequest } from "fastify";
import { Readable } from "node:stream";
import { z } from "zod";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { logInfo } from "../plugins/logging";
import { fetchUpstreamPayload } from "../proxy";
import {
  bindGitSource,
  bindGitHubInstallation,
  bindGitHubPrivateAccess,
  createGitHubImport,
  fetchImportCapabilities,
  fetchImportJob,
  fetchImportLookup,
  updateImportJobControl,
} from "../contracts/engine-client";
import type {
  GitHubImportRequest,
  GitHubInstallationBindingRequest,
  GitHubPrivateAccessBindingRequest,
  GitSourceBindingRequest,
} from "@decisionatlas/engine-contract";

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

const gitSourceBindingSchema = z.object({
  provider: z.enum(["github", "gitlab", "gitee", "local"]),
  access_mode: z.enum(["public", "token", "local_path"]),
  repo: z.string().min(3),
  token: z.string().min(1).optional(),
  source_ref: z.string().min(1).optional(),
  source_label: z.string().min(1).optional(),
  workspace_slug: z.string().min(1).optional(),
});

const webhookHeadersSchema = z.object({
  "x-github-event": z.string().min(1),
  "x-github-delivery": z.string().min(1).optional(),
  "x-hub-signature-256": z.string().min(1).optional(),
});

type WebhookRequest = FastifyRequest & { rawWebhookBody?: Buffer };

export async function importsRoute(app: FastifyInstance) {
  // GitHub HMAC signatures cover the exact request bytes, not parsed/reformatted JSON.
  app.addHook("preParsing", async (request, _reply, payload) => {
    if (request.url.split("?")[0] !== "/imports/github/webhook") return payload;
    const chunks: Buffer[] = [];
    for await (const chunk of payload) chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    const raw = Buffer.concat(chunks);
    (request as WebhookRequest).rawWebhookBody = raw;
    const replay = Readable.from([raw]);
    Object.assign(replay, { receivedEncodedLength: raw.length });
    return replay;
  });
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
    const upstream = await fetchImportLookup(env.ENGINE_BASE_URL, query.data.repo, authHeaders, app.log);
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

    const payload: GitHubImportRequest = parsed.data;
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    logInfo(app.log, "github import requested", { job_id: "pending" });
    const upstream = await createGitHubImport(env.ENGINE_BASE_URL, payload, authHeaders, app.log);
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
    const body: GitHubInstallationBindingRequest = parsed.data;
    const upstream = await bindGitHubInstallation(env.ENGINE_BASE_URL, body, authHeaders, app.log);
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

    const payload: GitHubPrivateAccessBindingRequest = {
      repo: parsed.data.repo,
      token: parsed.data.token,
      ...(parsed.data.source_ref ? { source_ref: parsed.data.source_ref } : {}),
      ...(parsed.data.source_label ? { source_label: parsed.data.source_label } : {}),
      ...(parsed.data.workspace_slug ? { workspace_slug: parsed.data.workspace_slug } : {}),
    };
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await bindGitHubPrivateAccess(env.ENGINE_BASE_URL, payload, authHeaders, app.log);
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/imports/git-sources/bind", async (request, reply) => {
    const parsed = gitSourceBindingSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid Git source binding payload",
        issues: parsed.error.issues
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const body: GitSourceBindingRequest = parsed.data;
    const upstream = await bindGitSource(env.ENGINE_BASE_URL, body, authHeaders, app.log);
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
        body: (request as WebhookRequest).rawWebhookBody?.toString("utf8") ?? JSON.stringify(request.body ?? {})
      }),
      app.log,
      "POST /imports/github/webhook"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  // Explicit action routes: do not expose arbitrary Engine paths through a
  // catch-all action segment. Engine remains the source of authorization.
  for (const action of ["pause", "resume"] as const) {
    app.post(`/imports/:jobId/${action}`, async (request, reply) => {
      const params = z.object({ jobId: z.string().regex(/^[A-Za-z0-9_-]{1,128}$/) }).safeParse(request.params);
      if (!params.success) {
        return reply.status(400).send({
          error: "Invalid import job id",
          issues: params.error.issues
        });
      }

      const env = getEnv();
      const authHeaders = await authHeadersForRequest(request);
      const upstream = await updateImportJobControl(
        env.ENGINE_BASE_URL, params.data.jobId, action, authHeaders, app.log
      );
      return reply.status(upstream.status).send(upstream.payload);
    });
  }

  // Read-only capability contract: the Engine is the single source of truth
  // for whether pause/resume is enabled in this deployment.
  app.get("/imports/capabilities", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchImportCapabilities(env.ENGINE_BASE_URL, authHeaders, app.log);
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
    const upstream = await fetchImportJob(env.ENGINE_BASE_URL, params.data.jobId, authHeaders, app.log);
    return reply.status(upstream.status).send(upstream.payload);
  });
}
