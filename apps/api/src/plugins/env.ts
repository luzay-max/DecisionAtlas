import { z } from "zod";

const booleanish = z
  .union([z.boolean(), z.string()])
  .transform((value, ctx) => {
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
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must be a recognized boolean value" });
    return z.NEVER;
  });

const httpUrl = z.string().url().superRefine((value, ctx) => {
  if (value !== value.trim()) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must not contain surrounding whitespace" });
  }
  if (value.includes("?") || value.includes("#")) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must not contain a query or fragment" });
  }
  try {
    const parsed = new URL(value);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must use http or https" });
    }
    if (parsed.username || parsed.password) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must not contain credentials" });
    }
    if (parsed.search || parsed.hash) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must not contain a query or fragment" });
    }
  } catch {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must be an absolute HTTP(S) URL" });
  }
});

const corsOrigins = z.string().default("").superRefine((value, ctx) => {
  for (const entry of value.split(",").map((origin) => origin.trim()).filter(Boolean)) {
    try {
      const parsed = new URL(entry);
      if (!["http:", "https:"].includes(parsed.protocol)
        || parsed.username
        || parsed.password
        || parsed.origin !== entry
        || parsed.pathname !== "/"
        || parsed.search
        || parsed.hash
        || entry === "*") {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must contain exact HTTP(S) origins only" });
      }
    } catch {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "must contain valid HTTP(S) origins only" });
    }
  }
});

const envSchema = z.object({
  PORT: z.coerce.number().int().min(1).max(65535).default(3001),
  ENGINE_BASE_URL: httpUrl.default("http://localhost:8000"),
  AUTH_COOKIE_NAME: z.string().regex(/^[!#$%&'*+.^_`|~0-9A-Za-z-]{1,128}$/).default("decisionatlas_session"),
  AUTO_BOOTSTRAP_AUTH: booleanish.default(false),
  APP_ENV: z.enum(["development", "test", "production"]).default("development"),
  CORS_ALLOWED_ORIGINS: corsOrigins,
});

export type ApiEnv = z.infer<typeof envSchema>;

export function getEnv(env: NodeJS.ProcessEnv = process.env): ApiEnv {
  let parsed: ApiEnv;
  try {
    parsed = envSchema.parse(env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const names = [...new Set(error.issues.map((issue) => String(issue.path[0] ?? "environment")))];
      throw new Error(`Invalid API environment configuration: ${names.join(", ")}`);
    }
    throw new Error("Invalid API environment configuration");
  }

  if (parsed.APP_ENV === "production" && !env.ENGINE_BASE_URL?.trim()) {
    throw new Error("Invalid API environment configuration: ENGINE_BASE_URL is required in production");
  }
  if (
    parsed.APP_ENV === "production"
    && !parsed.CORS_ALLOWED_ORIGINS.split(",").some((origin) => origin.trim().length > 0)
  ) {
    throw new Error("Invalid API environment configuration: CORS_ALLOWED_ORIGINS is required in production");
  }
  if (parsed.APP_ENV === "production" && parsed.AUTO_BOOTSTRAP_AUTH) {
    throw new Error("Invalid API environment configuration: AUTO_BOOTSTRAP_AUTH must be false in production");
  }

  return parsed;
}
