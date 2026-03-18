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

export type WhyAnswerResponse = {
  status: string;
  question: string;
  answer: string;
  citations: Array<{
    decision_id?: number;
    source_ref_id?: number;
    quote: string;
    url: string | null;
  }>;
};

export type TimelineItem = {
  id: number;
  title: string;
  review_state: string;
  status: string;
  problem: string;
  chosen_option: string;
  tradeoffs: string;
  created_at: string | null;
};

export type DashboardSummary = {
  workspace_slug: string;
  import_status: string;
  artifact_count: number;
  decision_counts: {
    candidate: number;
    accepted: number;
    rejected: number;
    superseded: number;
  };
  recent_alerts: Array<{
    id: number;
    alert_type: string;
    summary: string;
    status: string;
  }>;
};

export type DriftAlertItem = {
  id: number;
  alert_type: string;
  summary: string;
  status: string;
  confidence_label: string;
  created_at: string | null;
  artifact: {
    id: number;
    type: string;
    title: string | null;
    url: string | null;
  } | null;
  decision: {
    id: number;
    title: string;
    review_state: string;
    chosen_option: string;
  } | null;
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

export async function askWhy(workspaceSlug: string, question: string): Promise<WhyAnswerResponse> {
  const response = await fetch(`${apiBaseUrl}/query/why`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({
      workspace_slug: workspaceSlug,
      question
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to answer why question");
  }
  return response.json();
}

export async function getTimeline(workspaceSlug: string): Promise<TimelineItem[]> {
  const response = await fetch(`${apiBaseUrl}/timeline?workspace_slug=${encodeURIComponent(workspaceSlug)}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to load timeline");
  }
  return response.json();
}

export async function getDashboardSummary(workspaceSlug: string): Promise<DashboardSummary> {
  const response = await fetch(
    `${apiBaseUrl}/dashboard/summary?workspace_slug=${encodeURIComponent(workspaceSlug)}`,
    { cache: "no-store" }
  );
  if (!response.ok) {
    throw new Error("Failed to load dashboard summary");
  }
  return response.json();
}

export async function getDriftAlerts(workspaceSlug: string): Promise<DriftAlertItem[]> {
  const response = await fetch(`${apiBaseUrl}/drift?workspace_slug=${encodeURIComponent(workspaceSlug)}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to load drift alerts");
  }
  return response.json();
}
