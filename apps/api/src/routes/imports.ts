import { FastifyInstance } from "fastify";
import { z } from "zod";
import { getEnv } from "../plugins/env";

const githubImportSchema = z.object({
  workspace_slug: z.string().min(1),
  repo: z.string().min(3)
});

export async function importsRoute(app: FastifyInstance) {
  app.post("/imports/github", async (request, reply) => {
    const parsed = githubImportSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({
        error: "Invalid request payload",
        issues: parsed.error.issues
      });
    }

    const payload = parsed.data;
    const env = getEnv();

    const response = await fetch(`${env.ENGINE_BASE_URL}/imports/github`, {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const json = await response.json();
    return reply.status(response.status).send(json);
  });
}
