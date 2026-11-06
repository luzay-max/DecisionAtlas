import { FastifyInstance } from "fastify";
import type { WhyRequest } from "@decisionatlas/engine-contract";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchWhy } from "../contracts/engine-client";

export async function queryRoute(app: FastifyInstance) {
  app.post<{ Body: WhyRequest }>("/query/why", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchWhy(env.ENGINE_BASE_URL, request.body, authHeaders, app.log);
    return reply.status(upstream.status).send(upstream.payload);
  });
}
