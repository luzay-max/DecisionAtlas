import { FastifyInstance } from "fastify";
import { z } from "zod";
import { authHeadersForRequest } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

const documentImportSchema = z.object({
  title: z.string().min(1),
  document_type: z.string().min(1),
  content: z.string().min(1),
  scope: z.string().min(1).optional(),
  status: z.string().min(1).optional(),
  source_path: z.string().min(1).optional(),
});

const reviewSchema = z.object({
  review_state: z.enum(["accepted", "rejected"]),
});

export async function governanceRoute(app: FastifyInstance) {
  app.post("/governance/documents", async (request, reply) => {
    const parsed = documentImportSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid governance document payload",
        issues: parsed.error.issues,
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/governance/documents`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(parsed.data),
      }),
      app.log,
      "POST /governance/documents"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/governance/documents", async (request, reply) => {
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/governance/documents`, { headers: authHeaders }),
      app.log,
      "GET /governance/documents"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/governance/rules", async (request, reply) => {
    const query = z.object({ review_state: z.string().min(1).optional() }).safeParse(request.query);
    if (!query.success) {
      return reply.status(400).send({
        error: "Invalid governance rules query",
        issues: query.error.issues,
      });
    }
    const params = query.data.review_state ? `?review_state=${encodeURIComponent(query.data.review_state)}` : "";
    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/governance/rules${params}`, { headers: authHeaders }),
      app.log,
      "GET /governance/rules"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/governance/rules/:draftId/review", async (request, reply) => {
    const params = z.object({ draftId: z.string().min(1) }).safeParse(request.params);
    const parsed = reviewSchema.safeParse(request.body);
    if (!params.success || !parsed.success) {
      return reply.status(400).send({
        error: "Invalid governance rule review payload",
      });
    }

    const env = getEnv();
    const authHeaders = await authHeadersForRequest(request);
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/governance/rules/${encodeURIComponent(params.data.draftId)}/review`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify(parsed.data),
      }),
      app.log,
      "POST /governance/rules/:draftId/review"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
