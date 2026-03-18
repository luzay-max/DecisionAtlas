export type ReviewDecision = {
  id: number;
  workspace_id: number;
  title: string;
  status: string;
  review_state: string;
  problem: string;
  context: string | null;
  constraints: string | null;
  chosen_option: string;
  tradeoffs: string;
  confidence: number;
};

export type SourceRef = {
  id: number;
  artifact_id: number;
  span_start: number | null;
  span_end: number | null;
  quote: string;
  url: string | null;
  relevance_score: number | null;
};

export type DecisionDetail = ReviewDecision & {
  source_refs: SourceRef[];
};

const apiBaseUrl = process.env.API_BASE_URL ?? "http://localhost:3001";

export async function getReviewQueue(workspaceSlug: string): Promise<ReviewDecision[]> {
  const response = await fetch(
    `${apiBaseUrl}/decisions?workspace_slug=${encodeURIComponent(workspaceSlug)}&review_state=candidate`,
    { cache: "no-store" }
  );
  if (!response.ok) {
    throw new Error("Failed to load review queue");
  }
  return response.json();
}

export async function getDecisionDetail(id: string): Promise<DecisionDetail> {
  const response = await fetch(`${apiBaseUrl}/decisions/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load decision detail");
  }
  return response.json();
}
