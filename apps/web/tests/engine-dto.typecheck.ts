import type {
  DecisionDetail as EngineDecisionDetail,
  DecisionListItem,
  DecisionReviewResponse,
  WhyRequest,
  WhyResponse,
} from "@decisionatlas/engine-contract";
import type {
  DecisionDetail,
  DecisionReviewResult,
  ReviewDecision,
  WhyAnswerResponse,
} from "../lib/api";

export function webUsesEngineWhyContract(response: WhyAnswerResponse): WhyResponse {
  // @ts-expect-error unknown status must fail in the Web consumer too
  response.status = "accepted";
  // @ts-expect-error Web request must retain the Engine's required workspace
  const invalid: WhyRequest = { question: "why" };
  void invalid;
  return response;
}

export function webUsesEngineDecisionsContract(
  listItem: ReviewDecision,
  detail: DecisionDetail,
  reviewed: DecisionReviewResult,
): [DecisionListItem, EngineDecisionDetail, DecisionReviewResponse] {
  // @ts-expect-error a decision list item requires its evidence diagnostics
  const incomplete: ReviewDecision = { id: 1 };
  const detailContract: EngineDecisionDetail = detail;
  const reviewContract: DecisionReviewResponse = reviewed;
  // @ts-expect-error generated review response requires an audit event
  const invalidReview: DecisionReviewResponse = { ...reviewed, audit_event: undefined };
  void [incomplete, invalidReview];
  return [listItem, detailContract, reviewContract];
}
