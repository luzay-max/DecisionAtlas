import type { paths, components } from "./openapi.generated";
export type { paths, components, operations } from "./openapi.generated";

export type WhyRequest = paths["/query/why"]["post"]["requestBody"]["content"]["application/json"];
export type WhyResponse = paths["/query/why"]["post"]["responses"][200]["content"]["application/json"];
export type WhyStatus = components["schemas"]["WhyAnswerResponse"]["status"];
export type RetrievalMode = NonNullable<WhyResponse["retrieval_mode"]>;
export type WorkspaceReadiness = components["schemas"]["WorkspaceReadiness"];

export type DecisionListQuery = paths["/decisions"]["get"]["parameters"]["query"];
export type DecisionListItem = paths["/decisions"]["get"]["responses"][200]["content"]["application/json"][number];
export type DecisionDetail = paths["/decisions/{decision_id}"]["get"]["responses"][200]["content"]["application/json"];
export type DecisionReviewRequest = paths["/decisions/{decision_id}/review"]["post"]["requestBody"]["content"]["application/json"];
export type DecisionReviewResponse = paths["/decisions/{decision_id}/review"]["post"]["responses"][200]["content"]["application/json"];
export type DecisionSourceRef = components["schemas"]["DecisionSourceRefResponse"];
export type DecisionAuditEvent = components["schemas"]["DecisionAuditEventResponse"];
export type DecisionWorkspaceMode = DecisionListItem["workspace_mode"];

