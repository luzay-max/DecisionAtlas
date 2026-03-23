import { FastifyInstance } from "fastify";
import { z } from "zod";
import { getEnv } from "../plugins/env";
import { logInfo } from "../plugins/logging";
import { fetchUpstreamPayload } from "../proxy";

const githubImportSchema = z.object({
  workspace_slug: z.string().min(1).optional(),
  repo: z.string().min(3),
  mode: z.enum(["full", "since_last_sync"]).default("full")
});

export async function importsRoute(app: FastifyInstance) {
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
    logInfo(app.log, "github import requested", { job_id: "pending" });

    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/github`, {
        method: "POST",
        headers: {
          "content-type": "application/json"
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

  app.get("/imports/:jobId", async (request, reply) => {
    const params = z.object({ jobId: z.string().min(1) }).safeParse(request.params);
    if (!params.success) {
      return reply.status(400).send({
        error: "Invalid import job id",
        issues: params.error.issues
      });
    }

    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/imports/${params.data.jobId}`),
      app.log,
      "GET /imports/:jobId"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
