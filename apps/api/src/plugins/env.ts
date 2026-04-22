import { z } from "zod";

const booleanish = z
  .union([z.boolean(), z.string()])
  .transform((value) => {
    if (typeof value === "boolean") {
      return value;
    }
    const normalized = value.trim().toLowerCase();
    if (["1", "true", "yes", "on"].includes(normalized)) {
      return true;
    }
    if (["0", "false", "no", "off", ""].includes(normalized)) {
      return false;
    }
    throw new Error(`Invalid boolean value: ${value}`);
  });

const envSchema = z.object({
  PORT: z.coerce.number().default(3001),
  ENGINE_BASE_URL: z.string().url().default("http://localhost:8000"),
  AUTH_COOKIE_NAME: z.string().min(1).default("decisionatlas_session"),
  AUTO_BOOTSTRAP_AUTH: booleanish.default(false),
});

export type ApiEnv = z.infer<typeof envSchema>;

export function getEnv(env: NodeJS.ProcessEnv = process.env): ApiEnv {
  return envSchema.parse(env);
}
