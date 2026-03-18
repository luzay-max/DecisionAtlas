import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";

export async function driftRoute(app: FastifyInstance) {
  app.get("/drift", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const response = await fetch(`${env.ENGINE_BASE_URL}/drift?${query}`);
    const json = await response.json();
    return reply.status(response.status).send(json);
  });

  app.post("/drift/evaluate", async (request, reply) => {
    const env = getEnv();
    const response = await fetch(`${env.ENGINE_BASE_URL}/drift/evaluate`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(request.body),
    });
    const json = await response.json();
    return reply.status(response.status).send(json);
  });
}
