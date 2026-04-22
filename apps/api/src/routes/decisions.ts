import { FastifyInstance } from "fastify";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function decisionsRoute(app: FastifyInstance) {
  app.get("/decisions", async (request, reply) => {
    const env = getEnv();
    const query = new URLSearchParams(request.query as Record<string, string>).toString();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/decisions?${query}`, { headers: authHeaders }),
      app.log,
      "GET /decisions"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/decisions/:id", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/decisions/${id}`, { headers: authHeaders }),
      app.log,
      "GET /decisions/:id"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/decisions/:id/review", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/decisions/${id}/review`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(request.body)
      }),
      app.log,
      "POST /decisions/:id/review"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
