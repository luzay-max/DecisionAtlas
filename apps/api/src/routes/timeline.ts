import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";

export async function timelineRoute(app: FastifyInstance) {
  app.get("/timeline", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const response = await fetch(`${env.ENGINE_BASE_URL}/timeline?${query}`);
    const json = await response.json();
    return reply.status(response.status).send(json);
  });
}
