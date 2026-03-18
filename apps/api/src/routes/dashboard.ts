import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";

export async function dashboardRoute(app: FastifyInstance) {
  app.get("/dashboard/summary", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const response = await fetch(`${env.ENGINE_BASE_URL}/dashboard/summary?${query}`);
    const json = await response.json();
    return reply.status(response.status).send(json);
  });
}
