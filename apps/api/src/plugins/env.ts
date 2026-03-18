import { z } from "zod";

const envSchema = z.object({
  PORT: z.coerce.number().default(3001),
  ENGINE_BASE_URL: z.string().url().default("http://localhost:8000")
});

export type ApiEnv = z.infer<typeof envSchema>;

export function getEnv(env: NodeJS.ProcessEnv = process.env): ApiEnv {
  return envSchema.parse(env);
}
