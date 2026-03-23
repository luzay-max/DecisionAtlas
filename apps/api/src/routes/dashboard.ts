import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function dashboardRoute(app: FastifyInstance) {
  app.get("/dashboard/summary", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/dashboard/summary?${query}`),
      app.log,
      "GET /dashboard/summary"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
