import { FastifyInstance } from "fastify";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function driftRoute(app: FastifyInstance) {
  app.get("/drift", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const upstream = await fetchUpstreamPayload(fetch(`${env.ENGINE_BASE_URL}/drift?${query}`), app.log, "GET /drift");
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/drift/evaluate", async (request, reply) => {
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/drift/evaluate`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify(request.body),
      }),
      app.log,
      "POST /drift/evaluate"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
