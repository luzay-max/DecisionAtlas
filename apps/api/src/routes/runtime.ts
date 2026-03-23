import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function runtimeRoute(app: FastifyInstance) {
  app.get("/runtime/provider-mode", async (request, reply) => {
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/runtime/provider-mode`),
      app.log,
      "GET /runtime/provider-mode"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/runtime/provider-mode", async (request, reply) => {
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/runtime/provider-mode`, {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify(request.body)
      }),
      app.log,
      "POST /runtime/provider-mode"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
