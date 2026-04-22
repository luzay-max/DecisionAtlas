import { FastifyInstance } from "fastify";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function dashboardRoute(app: FastifyInstance) {
  app.get("/dashboard/summary", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/dashboard/summary?${query}`, { headers: authHeaders }),
      app.log,
      "GET /dashboard/summary"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
