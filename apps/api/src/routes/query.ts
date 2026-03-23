import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function queryRoute(app: FastifyInstance) {
  app.post("/query/why", async (request, reply) => {
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/query/why`, {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify(request.body)
      }),
      app.log,
      "POST /query/why"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
