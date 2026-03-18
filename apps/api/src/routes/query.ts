import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";

export async function queryRoute(app: FastifyInstance) {
  app.post("/query/why", async (request, reply) => {
    const env = getEnv();
    const response = await fetch(`${env.ENGINE_BASE_URL}/query/why`, {
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
