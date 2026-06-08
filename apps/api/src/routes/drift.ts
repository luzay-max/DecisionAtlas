import { FastifyInstance } from "fastify";
import { z } from "zod";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

const driftDispositionSchema = z.object({
  status: z.enum(["open", "acknowledged", "resolved", "false_positive"]),
  rationale: z.string().optional(),
});

export async function driftRoute(app: FastifyInstance) {
  app.get("/drift", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/drift?${query}`, { headers: authHeaders }),
      app.log,
      "GET /drift"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/drift/evaluate", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/drift/evaluate`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(request.body),
      }),
      app.log,
      "POST /drift/evaluate"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/drift/alerts/:alertId/disposition", async (request, reply) => {
    const params = z.object({ alertId: z.coerce.number().int().positive() }).safeParse(request.params);
    const parsed = driftDispositionSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({
        error: "Invalid drift disposition payload",
        issues: [...(params.success ? [] : params.error.issues), ...(parsed.success ? [] : parsed.error.issues)],
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/drift/alerts/${params.data.alertId}/disposition`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(parsed.data),
      }),
      app.log,
      "POST /drift/alerts/:alertId/disposition"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
