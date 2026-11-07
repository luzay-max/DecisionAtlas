import type { paths, components } from "./openapi.generated";
export type { paths, components, operations } from "./openapi.generated";

export type WhyRequest = paths["/query/why"]["post"]["requestBody"]["content"]["application/json"];
export type WhyResponse = paths["/query/why"]["post"]["responses"][200]["content"]["application/json"];
export type WhyStatus = components["schemas"]["WhyAnswerResponse"]["status"];
export type RetrievalMode = NonNullable<WhyResponse["retrieval_mode"]>;
export type WorkspaceReadiness = components["schemas"]["WorkspaceReadiness"];
