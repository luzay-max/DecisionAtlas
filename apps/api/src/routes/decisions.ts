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
    // Fastify exposes path params as strings. The cast is type-only so the
    // Engine retains its existing integer parsing and 422 error payload.
    const upstream = await fetchDecisionDetail(
      env.ENGINE_BASE_URL,
      id as unknown as number,
      authHeaders,
      app.log,
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/decisions/:id/review", async (request, reply) => {
    const env = getEnv();
    const { id } = request.params as { id: string };
    const authHeaders = await authHeadersForRequest(request);
    // Preserve the raw path token for the Engine's existing validation.
    const upstream = await fetchDecisionReview(
      env.ENGINE_BASE_URL,
      id as unknown as number,
      request.body as DecisionReviewRequest,
      authHeaders,
      app.log,
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
