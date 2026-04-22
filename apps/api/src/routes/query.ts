import { FastifyInstance } from "fastify";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

export async function queryRoute(app: FastifyInstance) {
  app.post("/query/why", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/query/why`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(request.body)
      }),
      app.log,
      "POST /query/why"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
