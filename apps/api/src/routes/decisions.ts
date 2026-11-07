import { FastifyInstance } from "fastify";
import type { DecisionListQuery, DecisionReviewRequest } from "@decisionatlas/engine-contract";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import {
  fetchDecisionDetail,
  fetchDecisionReview,
  fetchDecisionsList,
} from "../contracts/engine-client";

export async function decisionsRoute(app: FastifyInstance) {
  app.get("/decisions", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchDecisionsList(
      env.ENGINE_BASE_URL,
      request.query as DecisionListQuery,
      authHeaders,
      app.log,
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/decisions/:id", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchDecisionDetail(
      env.ENGINE_BASE_URL,
      Number(id),
      authHeaders,
      app.log,
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/decisions/:id/review", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchDecisionReview(
      env.ENGINE_BASE_URL,
      Number(id),
      request.body as DecisionReviewRequest,
      authHeaders,
      app.log,
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
