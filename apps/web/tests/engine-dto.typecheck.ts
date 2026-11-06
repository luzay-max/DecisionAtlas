import type { WhyResponse, WhyRequest } from "@decisionatlas/engine-contract";
import type { WhyAnswerResponse } from "../lib/api";

export function webUsesEngineContract(response: WhyAnswerResponse): WhyResponse {
  // @ts-expect-error unknown status must fail in the Web consumer too
  response.status = "accepted";
  // @ts-expect-error Web request must retain the Engine's required workspace
  const invalid: WhyRequest = { question: "why" };
  void invalid;
  return response;
}
