import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";

export async function decisionsRoute(app: FastifyInstance) {
  app.get("/decisions", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const response = await fetch(`${env.ENGINE_BASE_URL}/decisions?${query}`);
    const json = await response.json();
    return reply.status(response.status).send(json);
  });

  app.get("/decisions/:id", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const response = await fetch(`${env.ENGINE_BASE_URL}/decisions/${id}`);
    const json = await response.json();
    return reply.status(response.status).send(json);
  });

  app.post("/decisions/:id/review", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const response = await fetch(`${env.ENGINE_BASE_URL}/decisions/${id}/review`, {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify(request.body)
    });
    const json = await response.json();
    return reply.status(response.status).send(json);
  });
}
