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

export type ReviewState = "candidate" | "accepted" | "rejected" | "superseded";

export type WorkspaceMode = "demo" | "imported" | "mixed";

export type WorkspaceProvenance = {
  workspace_mode: WorkspaceMode;
  source_summary: string;
};

export type WorkspaceReadiness = {
  state: string;
  next_action: string;
  why_state: string;
  drift_state: string;
};

export type DriftEvaluation = {
  state: string;
  can_evaluate: boolean;
  next_action: string;
  last_evaluated_at: string | null;
  evaluated_rules?: number | null;
  created_alerts?: number | null;
};

export type ImportSummary = {
  stage?: string;
  outcome?: string;
  failure_category?: string;
  artifact_counts?: {
    issue: number;
    pr: number;
    commit: number;
    doc: number;
  } | null;
  document_summary?: {
    selected: number;
    imported: number;
    skipped: Record<string, number>;
    categories?: Record<string, number>;
  } | null;
  evidence_summary?: {
    reviewable_decisions: number;
    decision_source_types: Record<string, number>;
    contributing_doc_categories: Record<string, number>;
    contributing_doc_paths: string[];
  } | null;
  extraction_summary?: {
    shortlisted_artifacts?: number;
    screened_artifacts?: number;
    screened_in_artifacts?: number;
    screened_out_artifacts?: number;
    full_extraction_requests?: number;
    completed_full_extractions?: number;
    total_artifacts: number;
    processed_artifacts: number;
    created_candidates: number;
    salvaged_candidates?: number;
    skipped_provider_400: number;
    skipped_provider_timeout: number;
    skipped_invalid_json: number;
    selected_extraction_families?: Record<string, number>;
    conversion_loss_reasons?: Record<string, number>;
    elapsed_seconds?: number | null;
    estimated_remaining_seconds?: number | null;
    average_full_extraction_latency_ms?: number | null;
    current_artifact_title?: string | null;
    current_phase?: string | null;
    current_extraction_family?: string | null;
  } | null;
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

export type DecisionDetail = ReviewDecision &
  WorkspaceProvenance & {
  source_refs: SourceRef[];
};

export type WhyAnswerResponse = {
  status: string;
  question: string;
  answer: string;
  primary_decision?: {
    decision_id: number;
    title: string;
  };
  supporting_context?: Array<{
    decision_id: number;
    title: string;
    answer: string;
  }>;
  answer_context: WorkspaceProvenance & {
    workspace_readiness?: WorkspaceReadiness | null;
  };
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

export type TimelineResponse = WorkspaceProvenance & {
  items: TimelineItem[];
};

export type DashboardSummary = WorkspaceProvenance & {
  workspace_slug: string;
  repo_url: string | null;
  github_repo: string;
  import_status: string;
  latest_import: {
    job_id: string;
    workspace_slug?: string | null;
    repo?: string | null;
    mode: string;
    status: string;
    imported_count: number;
    summary?: ImportSummary | null;
    error_message: string | null;
    started_at: string | null;
    finished_at: string | null;
  } | null;
  artifact_count: number;
  decision_counts: {
    candidate: number;
    accepted: number;
    rejected: number;
    superseded: number;
  };
  workspace_readiness?: WorkspaceReadiness | null;
  drift_status?: DriftEvaluation | null;
  recent_alerts: Array<{
    id: number;
    alert_type: string;
    summary: string;
    status: string;
  }>;
};

export type DriftAlertsResponse = WorkspaceProvenance & {
  evaluation?: DriftEvaluation | null;
  alerts: DriftAlertItem[];
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

export type ImportResult = {
  job_id: string;
  workspace_slug?: string | null;
  repo?: string;
  mode?: string;
  status?: string;
  imported_count: number;
  summary?: ImportSummary | null;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
};

export type DriftEvaluationResult = {
  status: string;
  workspace_slug: string;
  evaluated_rules: number;
  created_alerts: number;
  evaluation?: DriftEvaluation | null;
};

export type ProviderModeState = {
  mode: string;
  is_live: boolean;
  llm_provider_mode: string;
  embedding_provider_mode: string;
  override_active: boolean;
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

export async function reviewDecision(decisionId: number, reviewState: ReviewState): Promise<ReviewDecision> {
  const response = await fetch(`${apiBaseUrl}/decisions/${decisionId}/review`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({
      review_state: reviewState
    })
  });
  if (!response.ok) {
    throw new Error("Failed to update decision review state");
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

export async function getTimeline(workspaceSlug: string): Promise<TimelineResponse> {
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

export async function getDriftAlerts(workspaceSlug: string): Promise<DriftAlertsResponse> {
  const response = await fetch(`${apiBaseUrl}/drift?workspace_slug=${encodeURIComponent(workspaceSlug)}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Failed to load drift alerts");
  }
  return response.json();
}

export async function evaluateDrift(workspaceSlug: string): Promise<DriftEvaluationResult> {
  const response = await fetch(`${apiBaseUrl}/drift/evaluate`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({ workspace_slug: workspaceSlug })
  });
  if (!response.ok) {
    throw new Error("Failed to evaluate drift");
  }
  return response.json();
}

export async function startGithubImport(workspaceSlug: string | null, repo: string): Promise<ImportResult> {
  const response = await fetch(`${apiBaseUrl}/imports/github`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify(
      workspaceSlug
        ? {
            workspace_slug: workspaceSlug,
            repo,
            mode: "full"
          }
        : {
            repo,
            mode: "full"
          }
    )
  });
  if (!response.ok) {
    throw new Error("Failed to start GitHub import");
  }
  return response.json();
}

export async function getImportJob(jobId: string): Promise<ImportResult> {
  const response = await fetch(`${apiBaseUrl}/imports/${jobId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load import job");
  }
  return response.json();
}

export async function getProviderMode(): Promise<ProviderModeState> {
  const response = await fetch(`${apiBaseUrl}/runtime/provider-mode`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load provider mode");
  }
  return response.json();
}

export async function setProviderMode(mode: "fake" | "live"): Promise<ProviderModeState> {
  const response = await fetch(`${apiBaseUrl}/runtime/provider-mode`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({ mode })
  });
  if (!response.ok) {
    throw new Error("Failed to update provider mode");
  }
  return response.json();
}
