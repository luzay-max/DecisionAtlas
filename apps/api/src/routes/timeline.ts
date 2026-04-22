import { FastifyInstance } from "fastify";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function timelineRoute(app: FastifyInstance) {
  app.get("/timeline", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/timeline?${query}`, { headers: authHeaders }),
      app.log,
      "GET /timeline"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
